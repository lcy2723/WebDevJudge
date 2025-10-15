import logging
import json
import os
import pyautogui
from openai import OpenAI
from openai import APITimeoutError, BadRequestError, InternalServerError, RateLimitError
from typing import Optional
from ui_tars.action_parser import parse_action_to_structure_output
from evaluator.gui_utils import parsing_response_to_pyautogui_code
from prompts.agent_prompt import PROMPT_CUA_STATIC, PROMPT_CUA_DYNAMIC, PROMPT_CUA_INTENTION
from utils.basic import encode_image


config = json.load(open("api_keys/config.json"))
config = config["ui_tars"]


def setup_logger(name="UITARS"):
    """Set up thread-safe logger"""
    logger = logging.getLogger(name)
    if not logger.handlers:  # Avoid adding handlers repeatedly
        logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter with process ID and timestamp
        formatter = logging.Formatter(
            '[PID:%(process)d] %(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    return logger


GUI_WIDTH, GUI_HEIGHT = pyautogui.size()


class UITARS:
    def __init__(
        self,
        # Model settings
        model: str = "doubao-1-5-ui-tars-250428",
        model_type: str = "doubao",
        # Generation settings
        max_tokens: int = 3000,
        top_p: Optional[float] = None,
        temperature:float = 0.0,
        # History settings
        max_image_history_length: Optional[int] = 5,
        max_steps: int = 15,
        # specific settings
        use_thinking: bool = False,
        language: str = "English",
        task_type: str = "static",
    ):
        self.model = model
        self.model_type = model_type
        self.client = OpenAI(
            base_url=config["base_url"],
            api_key=config["api_key"]
        )

        self.language = language

        self.thoughts = []
        self.actions = []
        self.observations = []
        self.history_images = []
        self.messages = []
        self.task_type = task_type

        if task_type == "static":
            self.prompt = PROMPT_CUA_STATIC
        elif task_type == "dynamic":
            self.prompt = PROMPT_CUA_DYNAMIC
        elif task_type == "intention":
            self.prompt = PROMPT_CUA_INTENTION
        else:
            raise ValueError(f"Invalid task type: {task_type}")
        self.action_parse_res_factor = 1000
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.temperature = temperature
        self.max_image_history_length = max_image_history_length
        self.max_steps = max_steps
        self.use_thinking = use_thinking if self.model_type == "doubao" else False
        self.language = language
        self.logger = setup_logger(f"UITARS_{os.getpid()}")
        self.logger.info(f"GUI size: {GUI_WIDTH}x{GUI_HEIGHT}")
        self.logger.info(f"Model: {self.model}")
        self.logger.info(f"Model type: {self.model_type}")
        
    def predict(self, instruction, image_path, current_step, image_width=GUI_WIDTH, image_height=GUI_HEIGHT):
        if self.messages == []:
            initial_prompt = self.prompt.format(
                language=self.language,
                instruction=instruction
            )
            self.messages.append({
                "role": "user",
                "content": initial_prompt
            })
            self.logger.info("="*10 + " Role: user " + "="*10)
            self.logger.info(f"Prompt: {initial_prompt}")

        base64_image = encode_image(image_path)
        self.observations.append(base64_image)

        self.messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                }
            ]
        })
        # if reach the max_steps, tell the agents to finish
        if current_step == self.max_steps - 1:
            if self.task_type == "static":
                self.messages.append({
                    "role": "user",
                    "content": "You have reached the maximum number of steps. Your next action should be `finished` and the content should contain the IDs of the elements you have found."
                })
            elif self.task_type == "dynamic":
                self.messages.append({
                    "role": "user",
                    "content": "You have reached the maximum number of steps. Your next action should be `finished` and the content should be `success` if you think the task can be completed in another few steps. Otherwise, the content should be `failed`."
                })
            elif self.task_type == "intention":
                self.messages.append({
                    "role": "user",
                    "content": "You have reached the maximum number of steps. Your next action should be `finished` and the content should be `success` if you think the purpose is demonstrated or fulfilled. Otherwise, the content should be `failed`."
                })
        
        # maintain only the last max_image_history_length images in self.messages
        if len(self.observations) > self.max_image_history_length:
            self.observations.pop(0)
            first_image_idx = -1
            for i, msg in enumerate(self.messages):
                if (
                    msg["role"] == "user" and
                    isinstance(msg["content"], list) and
                    len(msg["content"]) > 0 and
                    isinstance(msg["content"][0], dict) and
                    msg["content"][0].get("type") == "image_url"
                ):
                    first_image_idx = i
                    break
            if first_image_idx != -1:
                self.messages.pop(first_image_idx)


        # get response from model, catch the error during the response
        try:
            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                top_p=self.top_p,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False,
                seed=None,
                stop=None,
                frequency_penalty=None,
                presence_penalty=None,
                extra_body={"thinking": {"type": "enabled"} if self.use_thinking else {"type": "disabled"}}
            )
            response = chat_completion.choices[0].message.content
            self.messages.append({
                "role": "assistant",
                "content": response
            })
            metadata = {
                "prompt_token_count": chat_completion.usage.prompt_tokens,
                "candidates_token_count": chat_completion.usage.completion_tokens,
                "thoughts_token_count": 0
            }
            
            self.logger.info("="*10 + " Role: assistant " + "="*10)
            if self.use_thinking:
                metadata["thoughts_token_count"] = chat_completion.usage.completion_tokens_details.reasoning_tokens
                reasoning_content = chat_completion.choices[0].message.reasoning_content
                self.logger.info(f"<thinking>{reasoning_content}</thinking>")
            self.logger.info(response)

            if response is None:
                self.logger.error("Received None response from VLM")
                return "NONE RESPONSE", self.messages, metadata
            
            # Process response and execute action
            try:
                parsed_dict = parse_action_to_structure_output(response, self.action_parse_res_factor, image_height, image_width, model_type=self.model_type)
                thought = parsed_dict[0]["thought"]
                self.thoughts.append(thought)
                pyautogui_code = parsing_response_to_pyautogui_code(parsed_dict, GUI_HEIGHT, GUI_WIDTH)
                if pyautogui_code == "DONE":
                    return "DONE", self.messages, metadata
                elif "# Unrecognized action type:" in pyautogui_code:
                    self.logger.error(f"Unrecognized action type: {pyautogui_code}")
                    return "UNRECOGNIZED ACTION TYPE", self.messages, metadata
                else:
                    return pyautogui_code, self.messages, metadata
            except Exception as e:
                self.logger.error(f"Error when parsing response from client, with error: {e}")
                return "PARSING RESPONSE ERROR", self.messages, metadata
                
        except (APITimeoutError, BadRequestError, InternalServerError, RateLimitError) as e:
            self.logger.error(f"Error when calling the UI Tars client, with error: {e}")
            return "SERVER ERROR", self.messages, metadata
            