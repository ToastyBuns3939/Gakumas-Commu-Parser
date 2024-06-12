import pandas as pd

def inject_translations(txt_path, xlsx_path, output_path):
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

    # Create a list of tuples with original and translated texts and names
    translation_pairs = list(zip(df['text'], df['translated text'], df['name'], df['translated name']))

    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(output_path, 'w', encoding='utf-8') as file:
        for line in lines:
            original_line = line.strip()

            # Inject translated names sequentially
            for original_text, translated_text, original_name, translated_name in translation_pairs:
                if f'name={original_name}' in original_line:
                    original_line = original_line.replace(f'name={original_name}', f'name={translated_name}')

            # Inject translated texts sequentially
            for original_text, translated_text, _, _ in translation_pairs:
                if f'text={original_text}' in original_line:
                    original_line = original_line.replace(f'text={original_text}', f'text={translated_text}')

            # Ensure that choice texts are not overwritten
            if '[choice' in original_line:
                for original_text, translated_text, _, _ in translation_pairs:
                    if f'choice text={original_text}' in original_line:
                        original_line = original_line.replace(f'choice text={original_text}', f'choice text={translated_text}')

            file.write(original_line + '\n')