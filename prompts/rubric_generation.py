RUBRIC_GENERATION_PROMPT = """## TASK DESCRIPTION
You are an expert software quality assurance (QA) analyst. Your task is to take a user query for a web development project and generate a structured, hierarchical rubric. This rubric will be used to evaluate a generated webpage in a verifiable, binary (implemented/not implemented) manner.

The output must be a single JSON object with ```json and ``` wrapped around it.

The JSON object must have three top-level keys: `intention`, `static`, and `dynamic`.

### JSON Structure Rules:

1. Each node in the tree must be a dictionary with two keys:

    - `description`: A string describing the feature or goal.
    - `children`: A list of child nodes, or None if it is a leaf node.

2. The `intention` section should capture the high-level purpose and core goals of the webpage. Descriptions should be concise and conceptual overviews of what the user wants to achieve.

3. The `static` section must detail all the non-interactive, visible elements of the webpage. Break down components into their smallest logical parts. For example, a "user profile card" should be broken down into "user image," "username," and "user bio."

4. The `dynamic` section describes all the interactive functionalities of the page. 

    - It must have exactly two children: one for "basic" interactions and one for "complex" interactions.
    - `basic`: These are simple, single-step user actions. Examples include typing into a text field, clicking a non-submitting button, or selecting a dropdown option.
    - `complex`: These are multi-step processes or actions that result in a significant change to the application's state. Examples include submitting a form, fetching data, filtering a list of items, or navigating to a new view after an action.


5. Verifiable Leaf Nodes: Every leaf node in the entire tree (where "children" is None) must describe a specific, atomic, and verifiable requirement. The description should be a clear statement that can be evaluated as "implemented" or "not implemented."

## Example:

### User Query:
Design a book review submission form with fields for rating, author, and a text area. Lay out a book review page with the title, author, rating, review text and a user profile image.

### Generated Rubric Tree (Your Output):
```json
{
    "intention": {
        "description": "The purpose of the web page.",
        "children": [
            {
                "description": "A web page for book reviews.",
                "children": null
            },
            {
                "description": "A form for submitting book reviews.",
                "children": null
            },
            {
                "description": "Display submitted reviews.",
                "children": null
            }
        ]
    },
    "static": {
        "description": "The static elements of the web page.",
        "children": [
            {
                "description": "The book review submission form.",
                "children": [
                    {
                        "description": "A field to input the book's rating.",
                        "children": null
                    },
                    {
                        "description": "A field to input the book's author.",
                        "children": null
                    },
                    
                    {
                        "description": "A text area for the review content.",
                        "children": null
                    }
                ]
            },
            {
                "description": "The displayed book review.",
                "children": [
                    {
                        "description": "Display the title of the book.",
                        "children": null
                    },
                    {
                        "description": "Display the author of the book.",
                        "children": null
                    },
                    {
                        "description": "Display the rating of the book.",
                        "children": null
                    },
                    {
                        "description": "Display the review text.",
                        "children": null
                    },
                    {
                        "description": "Display the reviewer's user profile image.",
                        "children": null
                    }
                ]
            }
        ]
    },
    "dynamic": {
        "description": "The interaction between the user and the web page.",
        "children": [
            {
                "description": "Basic user interactions.",
                "children": [
                    {
                        "description": "User can type text into the review text area.",
                        "children": null
                    },
                    {
                        "description": "User can select a value in the rating field.",
                        "children": null
                    },
                    {
                        "description": "User can type text into the author field.",
                        "children": null
                    }
                ]
            },
            {
                "description": "Complex user interactions.",
                "children": [
                    {
                        "description": "User can submit the book review form.",
                        "children": null
                    },
                    {
                        "description": "After submission, the new review is visible on the page.",
                        "children": null
                    }
                ]
            }
        ]
    }
}
```

Now, analyze the following user query and generate the rubric tree in the specified JSON format.

### User Query:
[INSERT USER QUERY HERE]
"""