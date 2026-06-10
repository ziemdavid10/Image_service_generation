import csv
import json
import os

input_path  = os.path.join(os.path.dirname(__file__), "dataset_metadata_IACimages.csv")
output_path = os.path.join(os.path.dirname(__file__), "dataset_metadata_IACimages.jsonl")

with open(input_path, encoding="utf-8") as csv_file, \
     open(output_path, "w", encoding="utf-8") as jsonl_file:

    reader = csv.DictReader(csv_file)
    for row in reader:
        jsonl_file.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"Conversion terminee -> {output_path}")
