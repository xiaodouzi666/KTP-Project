import json
import os

def txt_to_json_recursive(root_folder, output_file):
    """
    Recursively process all .txt files in all subfolders under the root folder
    and convert them into a structured JSON knowledge base.
    """
    knowledge_base = {}

    # Walk through all subdirectories and files in the root folder
    for folder_name, subfolders, file_names in os.walk(root_folder):
        # Use the folder name as the category
        category = os.path.basename(folder_name).strip()
        if not category or category.startswith("."):
            continue  # Skip hidden/system folders

        if category not in knowledge_base:
            knowledge_base[category] = []

        for file_name in file_names:
            if file_name.endswith(".txt"):  # Process only .txt files
                file_path = os.path.join(folder_name, file_name)
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                    for line_number, line in enumerate(lines, start=1):
                        line = line.strip()
                        
                        # Skip empty lines
                        if not line:
                            continue
                        
                        # Try to split by '|'
                        parts = line.split("|")
                        if len(parts) == 3:  # Valid entry
                            try:
                                entry = {
                                    "symptom": parts[0].strip(),
                                    "severity": int(parts[1].strip()),  # Convert severity to integer
                                    "recommendation": parts[2].strip()
                                }
                                knowledge_base[category].append(entry)
                            except ValueError:
                                print(f"Skipping invalid severity in {file_path} (line {line_number}): {line}")
                        else:
                            # Handle dialogue-like content
                            extracted_entry = extract_dialogue(line, file_path, line_number)
                            if extracted_entry:
                                knowledge_base[category].append(extracted_entry)
                            else:
                                print(f"Skipping unprocessable line in {file_path} (line {line_number}): {line}")

    # Save the knowledge base as a JSON file
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(knowledge_base, json_file, ensure_ascii=False, indent=4)

    print(f"Knowledge base saved to {output_file}")

def extract_dialogue(line, file_path, line_number):
    """
    Attempt to extract useful information from dialogue-like content.
    """
    if "Counselor:" in line:
        # Treat counselor's statement as a recommendation
        return {
            "symptom": "General concern or inquiry",
            "severity": 5,  # Default severity for dialogue
            "recommendation": line.replace("Counselor:", "").strip()
        }
    elif ":" in line:
        # Treat other statements as symptoms
        speaker, content = line.split(":", 1)
        return {
            "symptom": content.strip(),
            "severity": 5,  # Default severity for dialogue
            "recommendation": "N/A"
        }
    else:
        return None  # Unprocessable line

# Usage
root_folder = r"C:\Users\小豆子\Desktop\KTP-Project"  # Replace with your root folder path
output_file = "knowledge_base.json"  # Output JSON file path
txt_to_json_recursive(root_folder, output_file)
