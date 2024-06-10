import pandas as pd
import re
import os
import tkinter as tk
from tkinter import filedialog
import sys

def extract_lines(file_path):
    names = []
    texts = []
    types = []
    message_text_found = False
    narration_text_found = False
    choice_text_found = False

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('[message'):
                message_text_found = True
                line_type = 'message'
            elif line.startswith('[narration'):
                narration_text_found = True
                line_type = 'narration'
            elif '[choice' in line:
                choice_text_found = True
                line_type = 'choice'
            else:
                continue
            
            # Remove 'se', 'clip', and 'hide' fields if they exist
            line = re.sub(r'se=.*?\]', ']', line)
            line = re.sub(r'clip=.*?\]', ']', line)
            line = re.sub(r'hide=.*?\]', ']', line)
            
            # Extract [message text=], [narration text=], and [choice text=] fields
            text_matches = re.findall(r'\[(?:message|narration|choice) text=(.*?)\]', line)
            name_match = re.search(r'name=(.*?)\]', line)
            
            if text_matches:
                for jp_text in text_matches:
                    if not name_match:
                        names.append('')  # Append empty string if no name field found
                    else:
                        names.append(name_match.group(1))
                    texts.append(jp_text)
                    types.append(line_type)

    return names, texts, types, message_text_found, narration_text_found, choice_text_found

def save_to_excel(names, texts, types, output_path, worksheet_name):
    if os.path.exists(output_path):  # Check if output file already exists
        existing_df = pd.read_excel(output_path)  # Read existing Excel file
        existing_df['text'] = existing_df['text'].astype(str)
        existing_df['translated'] = existing_df['translated'].astype(str)
        existing_df['translated name'] = existing_df['translated name'].astype(str)
        existing_translation_pairs = list(zip(existing_df['text'], existing_df['translated'], existing_df['name'], existing_df['translated name'], existing_df.index))
        
        # Merge existing translations with new translations
        translation_pairs = []
        for original_text, translated_text, original_name, translated_name, index in existing_translation_pairs:
            if translated_text.strip() != '' or translated_name.strip() != '':  # Check if translated text or name is not empty
                translation_pairs.append((original_text, translated_text, original_name, translated_name, index))
        
        for name, text, line_type in zip(names, texts, types):
            text_already_exists = False
            for original_text, _, _, _, _ in translation_pairs:
                if text == original_text:
                    text_already_exists = True
                    break
            if not text_already_exists:
                translation_pairs.append((text, '', name, '', len(translation_pairs)))
    else:
        translation_pairs = [(text, '', name, '', index) for index, (text, name) in enumerate(zip(texts, names))]

    df = pd.DataFrame({
        'type': types,
        'name': [name.strip() for name in names],  # Strip trailing spaces from 'name'
        'translated name': ['{user}' if name.strip() == '{user}' else '' for name in names],  # Fill 'translated name' with '{user}' if 'name' is '{user}'
        'text': texts,
        'translated': ''  # Initialize translated column with empty strings
    })

    # Ensure 'text' column is treated as string
    df['text'] = df['text'].astype(str)

    # Remove "name=" from the "text" column
    df['text'] = df['text'].str.replace(r' name=.*$', '', regex=True)

    # Convert "\n" to line breaks in the "text" column
    df['text'] = df['text'].str.replace(r'\\n', '\n', regex=True)

    # Fill in existing translations
    for original_text, translated_text, original_name, translated_name, _ in translation_pairs:
        df.loc[df['text'] == original_text, 'translated'] = translated_text
        df.loc[df['name'] == original_name, 'translated name'] = translated_name

    # Create a Pandas Excel writer using xlsxwriter as the engine
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')

    # Write the DataFrame to the Excel file with the specified worksheet name
    df.to_excel(writer, index=False, sheet_name=worksheet_name)

    # Get the xlsxwriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets[worksheet_name]

    # Define a format for cell alignment and text wrapping
    Dialogue_format = workbook.add_format({'align': 'left', 'valign': 'top', 'text_wrap': True})
    name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

    # Set column widths
    worksheet.set_column('A:A', 15, name_format)  # type column
    worksheet.set_column('B:B', 15, name_format)  # name column
    worksheet.set_column('C:C', 15, name_format)  # translated name column
    worksheet.set_column('D:D', 60, Dialogue_format)  # text column
    worksheet.set_column('E:E', 60, Dialogue_format)  # translated column

    # Adjust row heights automatically based on the content
    for i, jp_text in enumerate(texts):
        line_breaks = jp_text.count('\n') + 1
        row_height = 15 * line_breaks  # Assuming default row height is 15 units
        worksheet.set_row(i + 1, row_height)

    # Close the Pandas Excel writer and save the Excel file
    writer.close()

def inject_translations(txt_path, xlsx_path, output_path):
    # Read the Excel file
    df = pd.read_excel(xlsx_path)

    # Ensure 'text', 'translated', 'name', and 'translated name' columns are treated as strings
    df['text'] = df['text'].astype(str)
    df['translated'] = df['translated'].astype(str)
    df['name'] = df['name'].astype(str)
    df['translated name'] = df['translated name'].astype(str)

    # Convert line breaks in 'text', 'translated', and 'translated name' columns to "\n"
    df['text'] = df['text'].str.replace('\n', '\\n', regex=False)
    df['translated'] = df['translated'].str.replace('\n', '\\n', regex=False)
    df['translated name'] = df['translated name'].str.replace('\n', '\\n', regex=False)

    # Create a list of tuples with original and translated texts and names along with their indexes
    translation_pairs = list(zip(df['text'], df['translated'], df['name'], df['translated name'], df.index))

    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(output_path, 'w', encoding='utf-8') as file:
        for line in lines:
            original_line = line.strip()
            for original_text, translated_text, original_name, translated_name, index in translation_pairs:
                # Use unique placeholders for replacement to avoid conflicts
                placeholder_text = f'{{{{PLACEHOLDER_TEXT_{index}}}}}'
                placeholder_name = f'{{{{PLACEHOLDER_NAME_{index}}}}}'
                original_line = original_line.replace(original_text, placeholder_text, 1)
                original_line = original_line.replace(original_name, placeholder_name, 1)
            
            # Replace placeholders with translated texts and names and add padding
            for _, translated_text, _, translated_name, index in translation_pairs:
                placeholder_text = f'{{{{PLACEHOLDER_TEXT_{index}}}}}'
                placeholder_name = f'{{{{PLACEHOLDER_NAME_{index}}}}}'
                translated_text_padded = translated_text + ' '  # Add one space of padding
                translated_name_padded = translated_name + ' '  # Add one space of padding
                original_line = original_line.replace(placeholder_text, translated_text_padded)
                original_line = original_line.replace(placeholder_name, translated_name_padded)

            file.write(original_line + '\n')

def main():
    root = tk.Tk()
    root.withdraw()

    while True:
        try:
            option = input("GAKUEN IDOLM@STER commu text conversion tool\n1: convert .txt files to .xlsx files\n2: inject translations from .xlsx to .txt files\n3: exit\nChoice: ").strip()
            
            if option == '1':
                input_folder = filedialog.askdirectory(title="Select the input folder containing .txt files")
                if not input_folder:
                    raise Exception("No input folder selected.")

                output_folder = filedialog.askdirectory(title="Select the output folder for .xlsx files")
                if not output_folder:
                    raise Exception("No output folder selected.")

                for file_name in os.listdir(input_folder):
                    if file_name.endswith('.txt'):
                        input_path = os.path.join(input_folder, file_name)
                        output_path = os.path.join(output_folder, os.path.splitext(file_name)[0] + '.xlsx')

                        names, texts, types, _, _, _ = extract_lines(input_path)
                        save_to_excel(names, texts, types, output_path, 'Sheet1')
                
                print("Conversion to .xlsx completed successfully.")

            elif option == '2':
                input_folder = filedialog.askdirectory(title="Select the input folder containing .txt files")
                if not input_folder:
                    raise Exception("No input folder selected.")

                xlsx_folder = filedialog.askdirectory(title="Select the folder containing .xlsx files")
                if not xlsx_folder:
                    raise Exception("No .xlsx folder selected.")

                output_folder = filedialog.askdirectory(title="Select the output folder for updated .txt files")
                if not output_folder:
                    raise Exception("No output folder selected.")

                for file_name in os.listdir(input_folder):
                    if file_name.endswith('.txt'):
                        txt_path = os.path.join(input_folder, file_name)
                        xlsx_path = os.path.join(xlsx_folder, os.path.splitext(file_name)[0] + '.xlsx')
                        output_path = os.path.join(output_folder, file_name)

                        inject_translations(txt_path, xlsx_path, output_path)
                
                print("Translation injection completed successfully.")

            elif option == '3':
                sys.exit(0)
            
            else:
                print("Invalid option. Please enter 1, 2, or 3.")
        
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()