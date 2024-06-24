import pandas as pd
import os

def inject_translations(txt_path, xlsx_path, output_path):
    # Check if the Excel file exists
    if not os.path.isfile(xlsx_path):
        print(f"Excel file not found: {xlsx_path}")
        return
    
    # Read the Excel file
    df = pd.read_excel(xlsx_path)

    # Ensure 'text', 'translated text', 'name', and 'translated name' columns are treated as strings
    df['text'] = df['text'].astype(str)
    df['translated text'] = df['translated text'].astype(str)
    df['name'] = df['name'].astype(str)
    df['translated name'] = df['translated name'].astype(str)

    # Replace line breaks in the "text" and "translated text" columns with the string "\n"
    df['text'] = df['text'].apply(lambda x: x.replace('\n', '\\n'))
    df['translated text'] = df['translated text'].apply(lambda x: x.replace('\n', '\\n'))

    # Create a list of tuples with original and translated texts and names, excluding empty 'translated text'
    translation_pairs = [(row['text'], row['translated text'], row['name'], row['translated name'])
                         for _, row in df.iterrows() if row['translated text'].strip()]

    # Check if the text file exists
    if not os.path.isfile(txt_path):
        print(f"Text file not found: {txt_path}")
        return

    # Read the text file
    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Open the output file for writing
    with open(output_path, 'w', encoding='utf-8') as file:
        for line in lines:
            original_line = line.strip()

            # Inject translations sequentially
            if '[message' in original_line:
                for original_text, translated_text, original_name, translated_name in list(translation_pairs):
                    if f'name={original_name}' in original_line and f'text={original_text}' in original_line and translated_text != 'nan' and translated_name != 'nan':
                        original_line = original_line.replace(f'name={original_name}', f'name={translated_name}')
                        original_line = original_line.replace(f'text={original_text}', f'text={translated_text}')
                        translation_pairs.remove((original_text, translated_text, original_name, translated_name))
                        break
            elif '[choice' in original_line or '[narration' in original_line:
                for original_text, translated_text, original_name, translated_name in list(translation_pairs):
                    if f'text={original_text}' in original_line and translated_text != 'nan':
                        original_line = original_line.replace(f'text={original_text}', f'text={translated_text}')
                        translation_pairs.remove((original_text, translated_text, original_name, translated_name))

            file.write(original_line + '\n')