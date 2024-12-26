import json
import tkinter as tk
from tkinter import filedialog, Text

# Function to extract "produceConditionDescription" fields from the JSON data
def extract_produce_condition_description(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    descriptions = []
    
    # Extract the "produceConditionDescription" field from each entry in the JSON array
    for entry in data:
        if "produceConditionDescription" in entry:
            descriptions.append(entry["produceConditionDescription"])
    
    return descriptions

# Function to save the extracted fields to another JSON file
def save_descriptions_to_file(descriptions, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(descriptions, file, ensure_ascii=False, indent=4)

# Function to open a file dialog, extract fields, and save them to another file
def open_file():
    input_filepath = filedialog.askopenfilename(
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )
    if not input_filepath:
        return

    descriptions = extract_produce_condition_description(input_filepath)
    
    if descriptions:
        output_filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if output_filepath:
            save_descriptions_to_file(descriptions, output_filepath)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"Descriptions saved to {output_filepath}")
        else:
            result_text.insert(tk.END, "Save operation was canceled.")
    else:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "No 'produceConditionDescription' fields found.")

# Set up the main application window
root = tk.Tk()
root.title("Extract and Save produceConditionDescription from JSON")

# Add a button to open the file dialog
open_button = tk.Button(root, text="Open JSON File", command=open_file)
open_button.pack(pady=20)

# Add a Text widget to display the results
result_text = Text(root, wrap="word", height=10, width=60)
result_text.pack(pady=10)

# Run the application
root.mainloop()