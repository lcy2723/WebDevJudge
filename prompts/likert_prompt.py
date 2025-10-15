LIKERT_PROMPT_SINGLE = """You are an expert Quality Assurance engineer specializing in web development. Your objective is to meticulously evaluate a web development task. You will be provided with the user's initial query and the solution ({input_type}). Based on these inputs, you will assess the quality of the solution across several key dimensions. For each sub-criteria, you must provide a rating on a 5-point Likert scale, where 1 represents "Very Poor" and 5 represents "Excellent". Be as objective as possible.

## Evaluation Criteria
1. Functional Correctness and Completeness
    - 1.1 **Core Functionality**: Evaluates if the primary features and requirements specified in the user query are implemented correctly and function as expected.
    - 1.2 **Content Accuracy and Completeness**: Assesses if all the required content (text, images, links, etc.) is present, accurate, and correctly placed as per the user's query.
    - 1.3 **Boundary Conditions and Corner Cases**: Examines the solution's behavior with unexpected or extreme user inputs.
    - 1.4 **Error Handling**: Evaluates the system's ability to handle errors gracefully. This includes providing clear, user-friendly error messages and preventing application crashes due to invalid operations.

2. User Interface Quality
    - 2.1 **Visual Consistency and Cohesion**: Assesses the consistency of design elements such as color schemes, typography, spacing, and component styling throughout the webpage.
    - 2.2 **Layout, Structure, and Responsiveness**: Evaluates the overall layout and structural organization of the content. This also critically assesses the responsiveness of the design across different screen sizes (desktop, tablet, mobile).
    - 2.3 **Aesthetic Appeal**: Assesses the overall visual appeal of the webpage. This includes the effective use of color, typography, imagery, and whitespace to create an engaging and modern user interface.

3. Code Quality
    - 3.1 **Readability and Maintainability**: Assesses the clarity and organization of the code. This includes proper indentation, meaningful variable names, comments where necessary, and a logical file structure.
    - 3.2 **Modularity and Reusability**: Evaluates whether the code is broken down into logical, reusable components or functions, avoiding monolithic structures and code duplication.
    - 3.3 **Scalability and Efficiency**: Assesses the efficiency of the code, as well as the ability to scale the codebase for future enhancements or new features.

4. Interactivity:
    - 4.1 **Effectiveness**: Assesses the functionality and user experience of interactive elements like buttons, forms, menus, and sliders. This includes visual feedback on user actions (e.g., hover states, loading indicators).
    - 4.2 **Logical Correctness**: Evaluates whether the application state changes correctly in response to user interactions.
    - 4.3 **Accessibility**: Evaluates how easy and intuitive it is for a user to navigate the webpage and interact with its elements to achieve their goals.

## User Query
{user_query}

## Code
```tsx
{code}
```
"""

LIKERT_OUTPUT_SINGLE = """\n\n## Output Format
Begin your evaluation by providing a short explanation. End your output with a json object wrapped with ```json at the beginning and ``` at the end. Use the sub-criterion id as the key and assign a score from 1 to 5 as the value. Do not include any other text after the json object.

Here is an example of the output format:
```json
{
    "1.1": 5,
    "1.2": 4,
    "1.3": 3,
    "1.4": 2,
    "2.1": 5,
    "2.2": 4,
    "2.3": 3,
    "3.1": 5,
    "3.2": 4,
    "3.3": 3,
    "4.1": 5,
    "4.2": 4,
    "4.3": 3
}
```
"""

CODE_ONLY_INPUT_SINGLE = "code of the webpage"
INPUT_SINGLE = "code of the web, and a screenshot of the initial state of the webpage"

LIKERT_PROMPT_PAIR = """You are an expert Quality Assurance engineer specializing in web development. Your objective is to meticulously evaluate and compare two different web development solutions for the same task. You will be provided with the user's initial query and the solutions ({input_type}). Based on these inputs, you will assess the quality of each solution across several key dimensions. For each sub-criteria, you must provide a rating on a 5-point Likert scale, where 1 represents "Very Poor" and 5 represents "Excellent". Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Be as objective as possible.

## Evaluation Criteria
1. Functional Correctness and Completeness
    - 1.1 **Core Functionality**: Evaluates if the primary features and requirements specified in the user query are implemented correctly and function as expected.
    - 1.2 **Content Accuracy and Completeness**: Assesses if all the required content (text, images, links, etc.) is present, accurate, and correctly placed as per the user's query.
    - 1.3 **Boundary Conditions and Corner Cases**: Examines the solution's behavior with unexpected or extreme user inputs.
    - 1.4 **Error Handling**: Evaluates the system's ability to handle errors gracefully. This includes providing clear, user-friendly error messages and preventing application crashes due to invalid operations.

2. User Interface Quality
    - 2.1 **Visual Consistency and Cohesion**: Assesses the consistency of design elements such as color schemes, typography, spacing, and component styling throughout the webpage.
    - 2.2 **Layout, Structure, and Responsiveness**: Evaluates the overall layout and structural organization of the content. This also critically assesses the responsiveness of the design across different screen sizes (desktop, tablet, mobile).
    - 2.3 **Aesthetic Appeal**: Assesses the overall visual appeal of the webpage. This includes the effective use of color, typography, imagery, and whitespace to create an engaging and modern user interface.

3. Code Quality
    - 3.1 **Readability and Maintainability**: Assesses the clarity and organization of the code. This includes proper indentation, meaningful variable names, comments where necessary, and a logical file structure.
    - 3.2 **Modularity and Reusability**: Evaluates whether the code is broken down into logical, reusable components or functions, avoiding monolithic structures and code duplication.
    - 3.3 **Scalability and Efficiency**: Assesses the efficiency of the code, as well as the ability to scale the codebase for future enhancements or new features.

4. Interactivity:
    - 4.1 **Effectiveness**: Assesses the functionality and user experience of interactive elements like buttons, forms, menus, and sliders. This includes visual feedback on user actions (e.g., hover states, loading indicators).
    - 4.2 **Logical Correctness**: Evaluates whether the application state changes correctly in response to user interactions.
    - 4.3 **Accessibility**: Evaluates how easy and intuitive it is for a user to navigate the webpage and interact with its elements to achieve their goals.

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


LIKERT_OUTPUT_PAIR = """\n\n## Output Format
Begin your evaluation by providing a short explanation. End your output with a json object wrapped with ```json at the beginning and ``` at the end. Use the sub-criterion id as the key. The value for each key should be a nested json object containing the scores for each solution, with "A" and "B" as keys. Do not include any other text after the json object.

Here is an example of the output format:
```json
{
    "1.1": {
        "A": 5,
        "B": 4
    },
    "1.2": {
        "A": 4,
        "B": 5
    },
    "1.3": {
        "A": 3,
        "B": 3
    },
    "1.4": {
        "A": 2,
        "B": 2
    },
    "2.1": {
        "A": 5,
        "B": 5
    },
    "2.2": {
        "A": 4,
        "B": 3
    },
    "2.3": {
        "A": 3,
        "B": 4
    },
    "3.1": {
        "A": 5,
        "B": 5
    },
    "3.2": {
        "A": 4,
        "B": 4
    },
    "3.3": {
        "A": 3,
        "B": 3
    },
    "4.1": {
        "A": 5,
        "B": 4
    },
    "4.2": {
        "A": 4,
        "B": 5
    },
    "4.3": {
        "A": 3,
        "B": 4
    }
}
```
"""

CODE_ONLY_INPUT_PAIR = "codes for both webpages A and B"
INPUT_PAIR = "codes for both webpages A and B, and screenshots of the initial state of both webpages"