STATIC_PROMPT_SINGLE = """You are an expert Quality Assurance engineer specializing in web development. Your objective is to meticulously evaluate a web development task based on a predefined rubric. You will be provided with the user's initial query, the solution ({input_type}), and a rubric focusing on the static elements of the webpage.

Based on these inputs, you will assess whether each requirement in the rubric is implemented in the solution. During your assessment, please note that the solution might use different terminology than the rubric. Consider a requirement met if the solution's feature is equivalent. For example, the required heading element is present on the webpage, though the exact text or symbol differs.

## User Query
{user_query}

## Code
```tsx
{code}
```
"""

STATIC_OUTPUT_SINGLE = """## Rubric: Static Elements
```json
{rubric}
```

## INSTRUCTIONS
Your task is to return a JSON object that mirrors the structure of the provided rubric. For each leaf node in the rubric (i.e., where "children" is null), you must add a new key "value" and assign it a boolean value: `true` if the requirement is met, and `false` otherwise.

## Output Format
Begin your evaluation by providing an explanation for your reasoning. End your output with a JSON object wrapped with ```json at the beginning and ``` at the end. Do not include any other text after the JSON object.

Here is an example of the output format:
```json
{{
    "description": "The static elements of the web page.",
    "children": [
        {{
            "description": "The book review submission form.",
            "children": [
                {{
                    "description": "A field to input the book's rating.",
                    "children": null,
                    "value": true
                }},
                {{
                    "description": "A field to input the book's author.",
                    "children": null,
                    "value": true
                }},
                {{
                    "description": "A text area for the review content.",
                    "children": null,
                    "value": false
                }}
            ]
        }}
    ]
}}
```
"""

DYNAMIC_PROMPT_SINGLE = """You are an expert Quality Assurance engineer specializing in web development. Your objective is to meticulously evaluate a web development task based on a predefined rubric. You will be provided with the user's initial query, the solution ({input_type}), and a rubric focusing on the dynamic and interactive elements of the webpage.

Based on these inputs, you will assess whether each requirement in the rubric is implemented in the solution. During your assessment, please note that the solution might use different terminology than the rubric. Consider a requirement met if the solution's feature is equivalent. For example, the required heading element is present on the webpage, though the exact text or symbol differs.

## User Query
{user_query}

## Code
```tsx
{code}
```
"""

DYNAMIC_OUTPUT_SINGLE = """## Rubric: Dynamic Elements
```json
{rubric}
```

## INSTRUCTIONS
Your task is to return a JSON object that mirrors the structure of the provided rubric. For each leaf node in the rubric (i.e., where "children" is null), you must add a new key "value" and assign it a boolean value: `true` if the requirement is met, and `false` otherwise.

## Output Format
Begin your evaluation by providing a short explanation for your reasoning. End your output with a JSON object wrapped with ```json at the beginning and ``` at the end. Do not include any other text after the JSON object.

Here is an example of the output format:
```json
{{
    "description": "The interaction between the user and the web page.",
    "children": [
        {{
            "description": "Basic user interactions.",
            "children": [
                {{
                    "description": "User can type text into the review text area.",
                    "children": null,
                    "value": true
                }}
            ]
        }},
        {{
            "description": "Complex user interactions.",
            "children": [
                {{
                    "description": "User can submit the book review form.",
                    "children": null,
                    "value": false
                }}
            ]
        }}
    ]
}}
```
"""

INTENT_PROMPT_SINGLE = """You are an expert Quality Assurance engineer specializing in web development. Your objective is to meticulously evaluate a web development task based on a predefined rubric. You will be provided with the user's initial query, the solution ({input_type}), and a rubric focusing on the high-level intentions and goals of the webpage.

Based on these inputs, you will assess whether each requirement in the rubric is implemented in the solution. During your assessment, please note that the solution might use different terminology than the rubric. Consider a requirement met if the solution's feature is equivalent. For example, the required heading element is present on the webpage, though the exact text or symbol differs.

## User Query
{user_query}

## Code
```tsx
{code}
```
"""

INTENT_OUTPUT_SINGLE = """## Rubric: Intention
```json
{rubric}
```

## INSTRUCTIONS
Your task is to return a JSON object that mirrors the structure of the provided rubric. For each leaf node in the rubric (i.e., where "children" is null), you must add a new key "value" and assign it a boolean value: `true` if the requirement is met, and `false` otherwise.

## Output Format
Begin your evaluation by providing an explanation for your reasoning. End your output with a JSON object wrapped with ```json at the beginning and ``` at the end. Do not include any other text after the JSON object.

Here is an example of the output format:
```json
{{
    "description": "The purpose of the web page.",
    "children": [
        {{
            "description": "A web page for book reviews.",
            "children": null,
            "value": true
        }},
        {{
            "description": "A form for submitting book reviews.",
            "children": null,
            "value": true
        }},
        {{
            "description": "Display submitted reviews.",
            "children": null,
            "value": false
        }}
    ]
}}
```
"""

STATIC_PROMPT_PAIR = """You are an expert Quality Assurance engineer specializing in web development. Your objective is to meticulously evaluate and compare two different web development solutions for the same task based on a predefined rubric. You will be provided with the user's initial query, two solutions ({input_type}), and a rubric focusing on the static elements of the webpage.

Based on these inputs, you will assess whether each requirement in the rubric is implemented in each of the two solutions. Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Be as objective as possible. During your assessment, please note that the solution might use different terminology than the rubric. Consider a requirement met if the solution's feature is equivalent. For example, the required heading element is present on the webpage, though the exact text or symbol differs.

## User Query
{user_query}

## Code A
```tsx
{code_a}
```

## Code B
```tsx
{code_b}
```
"""

STATIC_OUTPUT_PAIR = """## Rubric: Static Elements
```json
{rubric}
```

## INSTRUCTIONS
Your task is to return a JSON object that mirrors the structure of the provided rubric. For each leaf node in the rubric (i.e., where "children" is null), you must add a new key "value". The value for this key must be a string: "A" if solution A is better, "B" if solution B is better, or "tie" if they are of equal quality or both fail to meet the requirement.

## Output Format
Begin your evaluation by providing an explanation for your reasoning. End your output with a JSON object wrapped with ```json at the beginning and ``` at the end. Do not include any other text after the JSON object.

Here is an example of the output format:
```json
{{
    "description": "The static elements of the web page.",
    "children": [
        {{
            "description": "The book review submission form.",
            "children": [
                {{
                    "description": "A field to input the book's rating.",
                    "children": null,
                    "value": "tie"
                }},
                {{
                    "description": "A field to input the book's author.",
                    "children": null,
                    "value": "A"
                }},
                {{
                    "description": "A text area for the review content.",
                    "children": null,
                    "value": "B"
                }}
            ]
        }}
    ]
}}
```
"""

DYNAMIC_PROMPT_PAIR = """You are an expert Quality Assurance engineer specializing in web development. Your objective is to meticulously evaluate and compare two different web development solutions for the same task based on a predefined rubric. You will be provided with the user's initial query, two solutions ({input_type}), and a rubric focusing on the dynamic and interactive elements of the webpage.

Based on these inputs, you will assess whether each requirement in the rubric is implemented in each of the two solutions. Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Be as objective as possible. During your assessment, please note that the solution might use different terminology than the rubric. Consider a requirement met if the solution's feature is equivalent. For example, the required heading element is present on the webpage, though the exact text or symbol differs.

## User Query
{user_query}

## Code A
```tsx
{code_a}
```

## Code B
```tsx
{code_b}
```
"""

DYNAMIC_OUTPUT_PAIR = """## Rubric: Dynamic Elements
```json
{rubric}
```

## INSTRUCTIONS
Your task is to return a JSON object that mirrors the structure of the provided rubric. For each leaf node in the rubric (i.e., where "children" is null), you must add a new key "value". The value for this key must be a string: "A" if solution A is better, "B" if solution B is better, or "tie" if they are of equal quality or both fail to meet the requirement.

## Output Format
Begin your evaluation by providing an explanation for your reasoning. End your output with a JSON object wrapped with ```json at the beginning and ``` at the end. Do not include any other text after the JSON object.

Here is an example of the output format:
```json
{{
    "description": "The interaction between the user and the web page.",
    "children": [
        {{
            "description": "Basic user interactions.",
            "children": [
                {{
                    "description": "User can type text into the review text area.",
                    "children": null,
                    "value": "A"
                }}
            ]
        }},
        {{
            "description": "Complex user interactions.",
            "children": [
                {{
                    "description": "User can submit the book review form.",
                    "children": null,
                    "value": "tie"
                }}
            ]
        }}
    ]
}}
```
"""

INTENT_PROMPT_PAIR = """You are an expert Quality Assurance engineer specializing in web development. Your objective is to meticulously evaluate and compare two different web development solutions for the same task based on a predefined rubric. You will be provided with the user's initial query, two solutions ({input_type}), and a rubric focusing on the high-level intentions and goals of the webpage.

Based on these inputs, you will assess whether each requirement in the rubric is implemented in each of the two solutions. Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Be as objective as possible. During your assessment, please note that the solution might use different terminology than the rubric. Consider a requirement met if the solution's feature is equivalent. For example, the required heading element is present on the webpage, though the exact text or symbol differs.

## User Query
{user_query}

## Code A
```tsx
{code_a}
```

## Code B
```tsx
{code_b}
```
"""

INTENT_OUTPUT_PAIR = """## Rubric: Intention
```json
{rubric}
```

## INSTRUCTIONS
Your task is to return a JSON object that mirrors the structure of the provided rubric. For each leaf node in the rubric (i.e., where "children" is null), you must add a new key "value". The value for this key must be a string: "A" if solution A is better, "B" if solution B is better, or "tie" if they are of equal quality or both fail to meet the requirement.

## Output Format
Begin your evaluation by providing an short explanation for your reasoning. End your output with a JSON object wrapped with ```json at the beginning and ``` at the end. Do not include any other text after the JSON object.

Here is an example of the output format:
```json
{{
    "description": "The purpose of the web page.",
    "children": [
        {{
            "description": "A web page for book reviews.",
            "children": null,
            "value": "A"
        }},
        {{
            "description": "A form for submitting book reviews.",
            "children": null,
            "value": "B"
        }},
        {{
            "description": "Display submitted reviews.",
            "children": null,
            "value": "tie"
        }}
    ]
}}
```
"""

ALL_PROMPT_SINGLE = """You are an expert Quality Assurance engineer specializing in web development. Your objective is to meticulously evaluate a web development task based on a predefined rubric. You will be provided with the user's initial query, the solution ({input_type}), and a comprehensive rubric covering intention, static, and dynamic elements of the webpage.

Based on these inputs, you will assess whether each requirement in the rubric is implemented in the solution. During your assessment, please note that the solution might use different terminology than the rubric. Consider a requirement met if the solution's feature is equivalent. For example, the required heading element is present on the webpage, though the exact text or symbol differs.

## User Query
{user_query}

## Code
```tsx
{code}
```
"""

ALL_OUTPUT_SINGLE = """## Rubric
### Intention
```json
{intention_rubric}
```

### Static Elements
```json
{static_rubric}
```

### Dynamic Elements
```json
{dynamic_rubric}
```

## INSTRUCTIONS
Your task is to return a single JSON object. This object should have three top-level keys: "intention", "static", and "dynamic". The value for each key should be a JSON object that mirrors the structure of the corresponding rubric provided above. For each leaf node in each rubric (i.e., where "children" is null), you must add a new key "value" and assign it a boolean value: `true` if the requirement is met, and `false` otherwise.

## Output Format
Begin your evaluation by providing an explanation for your reasoning. End your output with a JSON object wrapped with ```json at the beginning and ``` at the end. Do not include any other text after the JSON object.

Here is an example of the output format:
```json
{{
    "intention": {{
        "description": "The purpose of the web page.",
        "children": [
            {{
                "description": "A web page for book reviews.",
                "children": null,
                "value": true
            }}
        ]
    }},
    "static": {{
        "description": "The static elements of the web page.",
        "children": [
            {{
                "description": "The book review submission form.",
                "children": [
                    {{
                        "description": "A field to input the book's rating.",
                        "children": null,
                        "value": true
                    }}
                ]
            }}
        ]
    }},
    "dynamic": {{
        "description": "The interaction between the user and the web page.",
        "children": [
            {{
                "description": "Basic user interactions.",
                "children": [
                    {{
                        "description": "User can type text into the review text area.",
                        "children": null,
                        "value": true
                    }}
                ]
            }}
        ]
    }}
}}
```
"""


ALL_PROMPT_PAIR = """You are an expert Quality Assurance engineer specializing in web development. Your objective is to meticulously evaluate and compare two different web development solutions for the same task based on a predefined rubric. You will be provided with the user's initial query, two solutions ({input_type}), and a comprehensive rubric covering intention, static, and dynamic elements of the webpage.

Based on these inputs, you will assess whether each requirement in the rubric is implemented in each of the two solutions. Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Be as objective as possible. During your assessment, please note that the solution might use different terminology than the rubric. Consider a requirement met if the solution's feature is equivalent. For example, the required heading element is present on the webpage, though the exact text or symbol differs.

## User Query
{user_query}

## Code A
```tsx
{code_a}
```

## Code B
```tsx
{code_b}
```
"""

ALL_OUTPUT_PAIR = """## Rubric
### Intention
```json
{intention_rubric}
```

### Static Elements
```json
{static_rubric}
```

### Dynamic Elements
```json
{dynamic_rubric}
```

## INSTRUCTIONS
Your task is to return a single JSON object. This object should have three top-level keys: "intention", "static", and "dynamic". The value for each key should be a JSON object that mirrors the structure of the corresponding rubric provided above. For each leaf node in each rubric (i.e., where "children" is null), you must add a new key "value". The value for this key must be a string: "A" if solution A is better, "B" if solution B is better, or "tie" if they are of equal quality or both fail to meet the requirement.

## Output Format
Begin your evaluation by providing an explanation for your reasoning. End your output with a JSON object wrapped with ```json at the beginning and ``` at the end. Do not include any other text after the JSON object.

Here is an example of the output format:
```json
{{
    "intention": {{
        "description": "The purpose of the web page.",
        "children": [
            {{
                "description": "A web page for book reviews.",
                "children": null,
                "value": "A"
            }}
        ]
    }},
    "static": {{
        "description": "The static elements of the web page.",
        "children": [
            {{
                "description": "The book review submission form.",
                "children": [
                    {{
                        "description": "A field to input the book's rating.",
                        "children": null,
                        "value": "tie"
                    }}
                ]
            }}
        ]
    }},
    "dynamic": {{
        "description": "The interaction between the user and the web page.",
        "children": [
            {{
                "description": "Basic user interactions.",
                "children": [
                    {{
                        "description": "User can type text into the review text area.",
                        "children": null,
                        "value": "B"
                    }}
                ]
            }}
        ]
    }}
}}
```
"""

CODE_ONLY_INPUT_SINGLE = "code of the webpage"
INPUT_SINGLE = "code of the web, and a screenshot of the initial state of the webpage"

CODE_ONLY_INPUT_PAIR = "codes for both webpages A and B"
INPUT_PAIR = "codes for both webpages A and B, and screenshots of the initial state of both webpages"