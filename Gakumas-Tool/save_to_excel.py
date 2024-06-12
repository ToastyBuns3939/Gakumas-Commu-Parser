import re
import pandas as pd
import os
from name_dictionary import name_translation_dict

def translate_names(names):
    # Translate names using the provided dictionary
    translated_names = [name_translation_dict.get(name.strip(), '') for name in names]
    return translated_names

def save_to_excel(names, texts, types, output_path, worksheet_name):
    existing_row_count = 0

    if os.path.exists(output_path):  # Check if output file already exists
        existing_df = pd.read_excel(output_path)  # Read existing Excel file
        existing_row_count = len(existing_df)  # Store the existing row count

        # Cast all columns to object dtype to ensure compatibility when replacing nan with ''
        existing_df = existing_df.astype(object)
        existing_df.fillna('', inplace=True)  # Replace nan with empty strings
        existing_df['text'] = existing_df['text'].astype(str)
        
        # Check and rename 'translated' column if it exists
        if 'translated' in existing_df.columns:
            existing_df.rename(columns={'translated': 'translated text'}, inplace=True)
        
        existing_df['translated text'] = existing_df['translated text'].astype(str)
        existing_df['translated name'] = existing_df['translated name'].astype(str)
        existing_translation_pairs = list(zip(existing_df['text'], existing_df['translated text'], existing_df['name'], existing_df['translated name'], existing_df.index))
        
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

    translated_names = translate_names(names)

    df = pd.DataFrame({
        'type': types,
        'name': [name.strip() for name in names],  # Strip trailing spaces from 'name'
        'translated name': [''] * len(names),  # Initialize translated name column
        'text': texts,
        'translated text': [''] * len(texts)  # Initialize translated column with empty strings
    })

    # Ensure 'text' column is treated as string
    df['text'] = df['text'].astype(str)

    # Remove "name=" from the "text" column
    df['text'] = df['text'].str.replace(r' name=.*$', '', regex=True)

    # Fill in existing translations
    for original_text, translated_text, original_name, translated_name, _ in translation_pairs:
        df.loc[df['text'] == original_text, 'translated text'] = translated_text
        df.loc[df['name'] == original_name, 'translated name'] = translated_name

    # Convert "\\n" to line breaks in the "text" column
    df['text'] = df['text'].str.replace(r'\\n', '\n', regex=True)

    # Update translated names
    for original_name, translated_name in zip(names, translated_names):
        df.loc[df['name'] == original_name, 'translated name'] = translated_name

    # Handle nan values by filling them with empty strings
    df = df.astype(object)  # Ensure all columns are treated as object dtype
    df.fillna('', inplace=True)

    new_row_count = len(df)  # Get the new row count

    # Only proceed to save the file if the row count has changed
    if existing_row_count != new_row_count:
        # Create a Pandas Excel writer using xlsxwriter as the engine
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')

        # Write the DataFrame to the Excel file with the specified worksheet name
        df.to_excel(writer, index=False, sheet_name=worksheet_name, na_rep='')

        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets[worksheet_name]

        # Define a format for cell alignment and text wrapping
        dialogue_format = workbook.add_format({'align': 'left', 'valign': 'top', 'text_wrap': True})
        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

        # Set column widths
        worksheet.set_column('A:A', 15, name_format)  # type column
        worksheet.set_column('B:B', 15, name_format)  # name column
        worksheet.set_column('C:C', 15, name_format)  # translated name column
        worksheet.set_column('D:D', 70, dialogue_format)  # text column
        worksheet.set_column('E:E', 70, dialogue_format)  # translated column

        # Adjust row heights automatically based on the content
        for i, jp_text in enumerate(df['text']):
            line_breaks = jp_text.count('\n') + 1
            row_height = 15 * line_breaks  # Assuming default row height is 15 units
            worksheet.set_row(i + 1, row_height)

        # Close the Pandas Excel writer and save the Excel file
        writer.close()