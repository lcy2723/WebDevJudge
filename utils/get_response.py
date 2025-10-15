import json
from openai import OpenAI


config = json.load(open("api_keys/config.json"))
def generate(model="gpt-4o", messages=None, generation_config={"max_tokens": 16384, "temperature": 0.0}):
    client = OpenAI(
        api_key=config[model]["api_key"],
        base_url=config[model]["base_url"],
    )
    response = client.chat.completions.create(
        model=config[model]["model"],
        messages=messages,
        max_tokens=generation_config["max_tokens"],
        temperature=generation_config["temperature"]
    )
    metadata = {
        "prompt_token_count": response.usage.prompt_tokens,
        "candidates_token_count": response.usage.completion_tokens,
        "thoughts_token_count": 0,
    }
    return response.choices[0].message.content, metadata