import json
import sys

# Check if the correct number of command-line arguments are provided
if len(sys.argv) != 3:
    print("Usage: python your_script_name.py <input_json_file> <output_json_file>")
    sys.exit(1)

input_file_name = sys.argv[1]
output_file_name = sys.argv[2]

try:
    # Load the input JSON file
    with open(input_file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: The input file '{input_file_name}' was not found.")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from the input file '{input_file_name}'. Please ensure it's a valid JSON file.")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred while reading the input file: {e}")
    sys.exit(1)

# Initialize an empty dictionary for the output
output_data = {}

# Process each subtitle entry if 'subtitles' key exists
if 'subtitles' in data:
    for subtitle in data.get('subtitles', []):
        # Keep all characters intact, including leading/trailing whitespace and newlines
        original_text = subtitle.get('text', '')
        
        # Placeholder for translation. As a live demo, I cannot perform actual translation.
        # User would need to integrate a translation API or manually translate.
        output_data[original_text] = "TRANSLATE_ME" # This will be the placeholder for the English translation

try:
    # Save the transformed data to the output JSON file
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"Processed data successfully saved to {output_file_name}")
except Exception as e:
    print(f"An error occurred while writing the output file: {e}")
    sys.exit(1)