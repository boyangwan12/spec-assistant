import json
import os

# Always use the correct path to the file
data_dir = os.path.dirname(__file__)
input_path = os.path.join(data_dir, 'response.json')
output_path = os.path.join(data_dir, 'embed_input.json')

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

texts = [el['text'] for el in data['elements'] if 'text' in el]

embed_payload = {
    "elements": texts
}

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(embed_payload, f, ensure_ascii=False, indent=2)

print(f"Prepared {output_path} for /embed endpoint.")