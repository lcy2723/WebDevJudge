# This code is modified from the UI-TARS project.
# https://github.com/bytedance/UI-TARS

PROMPT_CUA_STATIC = """You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task.

## Output Format
```
Thought: ...
Action: ...
```

## Action Space

click(point='<point>x1 y1</point>')
left_double(point='<point>x1 y1</point>')
right_single(point='<point>x1 y1</point>')
drag(start_point='<point>x1 y1</point>', end_point='<point>x2 y2</point>')
hotkey(key='ctrl c') # Split keys with a space and use lowercase. Also, do not use more than 3 keys in one hotkey action.
type(content='xxx') # Use escape characters \\', \\\", and \\n in content part to ensure we can parse the content in normal python string format. If you want to submit your input, use \\n at the end of content. 
scroll(point='<point>x1 y1</point>', direction='down or up or right or left') # Show more information on the `direction` side.
wait() #Sleep for 5s and take a screenshot to check for any changes.
finished(content='xxx') # Use escape characters \\', \\", and \\n in content part to ensure we can parse the content in normal python string format.


## Note
- Use {language} in `Thought` part.
- Write a small plan and finally summarize your next action (with its target element) in one sentence in `Thought` part.
- If the task involves file uploads, you can only upload the 'sample_1.png', 'sample_2.png', 'sample.xlsx' or 'sample.pdf' files. Do not enter any other directories.

## User Instruction
{instruction}
"""

PROMPT_CUA_DYNAMIC = """You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task.

## Output Format
```
Thought: ...
Action: ...
```

## Action Space

click(point='<point>x1 y1</point>')
left_double(point='<point>x1 y1</point>')
right_single(point='<point>x1 y1</point>')
drag(start_point='<point>x1 y1</point>', end_point='<point>x2 y2</point>')
hotkey(key='ctrl c') # Split keys with a space and use lowercase. Also, do not use more than 3 keys in one hotkey action.
type(content='xxx') # Use escape characters \\', \\\", and \\n in content part to ensure we can parse the content in normal python string format. If you want to submit your input, use \\n at the end of content. 
scroll(point='<point>x1 y1</point>', direction='down or up or right or left') # Show more information on the `direction` side.
wait() #Sleep for 5s and take a screenshot to check for any changes.
finished(content='xxx') # Use escape characters \\', \\", and \\n in content part to ensure we can parse the content in normal python string format.


## Note
- Use {language} in `Thought` part.
- Write a small plan and finally summarize your next action (with its target element) in one sentence in `Thought` part.
- If you think the task is infeasible, you action should be `finished` and the content should be `failed` without any other content.
- If the task involves file uploads, you can only upload the 'sample_1.png', 'sample_2.png', 'sample.xlsx' or 'sample.pdf' files. Do not enter any other directories.

## User Instruction
{instruction}
"""

PROMPT_CUA_INTENTION = """You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task.

## Output Format
```
Thought: ...
Action: ...
```

## Action Space

click(point='<point>x1 y1</point>')
left_double(point='<point>x1 y1</point>')
right_single(point='<point>x1 y1</point>')
drag(start_point='<point>x1 y1</point>', end_point='<point>x2 y2</point>')
hotkey(key='ctrl c') # Split keys with a space and use lowercase. Also, do not use more than 3 keys in one hotkey action.
type(content='xxx') # Use escape characters \\', \\\", and \\n in content part to ensure we can parse the content in normal python string format. If you want to submit your input, use \\n at the end of content. 
scroll(point='<point>x1 y1</point>', direction='down or up or right or left') # Show more information on the `direction` side.
wait() #Sleep for 5s and take a screenshot to check for any changes.
finished(content='xxx') # Use escape characters \\', \\", and \\n in content part to ensure we can parse the content in normal python string format.


## Note
- Use {language} in `Thought` part.
- Write a small plan and finally summarize your next action (with its target element) in one sentence in `Thought` part.
- If the task involves file uploads, you can only upload the 'sample_1.png', 'sample_2.png', 'sample.xlsx' or 'sample.pdf' files. Do not enter any other directories.

## User Instruction
{instruction}
"""

STATIC_CHECKING_PROMPT = """Please check the given web page for a specific set of elements. Some elements may require an action to become accessible. Please perform necessary actions. Please note that the elements might use different terminology. Consider a element found if the feature is equivalent. For example, the required heading element is present on the webpage, though the exact text or symbol differs.

**Elements to Check:**
The elements are listed with their ID and a brief description. After checking, your action should be `finished` and the content should be the elements IDs you have found.

{static_elements}
"""

INTENTION_CHECKING_PROMPT = """Please determine if the given web page can fulfill or demonstrate the purpose. You are allowed to interact with the page, such as clicking buttons, filling forms, or navigating, to see if the purpose can be met or demonstrated.

**Purpose to Check:**
{intention}


After your evaluation, your action should be `finished`. If the webpage demonstrates or fulfills the purpose, the content should be `success`. Otherwise, the content should be `failed` without any other content.
"""