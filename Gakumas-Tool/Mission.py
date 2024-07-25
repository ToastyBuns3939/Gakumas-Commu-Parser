import json
import re
import tkinter as tk
from tkinter import filedialog, messagebox

def process_json(input_data):
    def process_line(key, value):
        # Remove commas from numbers and find the numbers
        numbers = re.findall(r'\d[\d,]*', key)
        if numbers:
            max_number = max(numbers, key=lambda x: int(x.replace(',', '')))
            plain_number = max_number.replace(',', '')
            return f"{key} ({plain_number}/{plain_number})", f"{value} ({plain_number}/{plain_number})"
        else:
            return f"{key} (1/1)", f"{value} (1/1)"
    
    data = json.loads(input_data)
    processed_data = {}
    for key, value in data.items():
        if " (" not in key:
            new_key, new_value = process_line(key, value)
            processed_data[new_key] = new_value
        else:
            processed_data[key] = value
    
    return json.dumps(processed_data, ensure_ascii=False, indent=4)

def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not file_path:
        return None
    with open(file_path, 'r', encoding='utf-8') as file:
        return file_path, file.read()

def save_file(data):
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if not file_path:
        return
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(data)
    messagebox.showinfo("Success", "File saved successfully")

def process_file():
    result = load_file()
    if result is None:
        return
    input_file_path, input_data = result
    processed_data = process_json(input_data)
    save_file(processed_data)

def create_gui():
    root = tk.Tk()
    root.title("JSON Processor")
    root.geometry("300x150")
    
    frame = tk.Frame(root)
    frame.pack(pady=20)

    process_button = tk.Button(frame, text="Process JSON File", command=process_file)
    process_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()