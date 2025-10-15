import base64
import re
import json


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        image = base64.b64encode(image_file.read()).decode('utf-8')
    return image


def extract_and_parse_json(response_str):
    matches = re.findall(r'```json(.*?)```', response_str, re.DOTALL)
    if matches:
        extracted_json = matches[-1].strip()
        return json.loads(extracted_json)
    raise ValueError("No JSON found in response")


