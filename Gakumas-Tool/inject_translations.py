# import pandas as pd
# 
# def inject_translations(txt_path, xlsx_path, output_path):
#     # Read the Excel file
#     df = pd.read_excel(xlsx_path)
# 
#     # Ensure 'text', 'translated text', 'name', and 'translated name' columns are treated as strings
#     df['text'] = df['text'].astype(str)
#     df['translated text'] = df['translated text'].astype(str)
#     df['name'] = df['name'].astype(str)
#     df['translated name'] = df['translated name'].astype(str)
# 
#     # Create a list of tuples with original and translated texts and names
#     translation_pairs = list(zip(df['text'], df['translated text'], df['name'], df['translated name']))
# 
#     with open(txt_path, 'r', encoding='utf-8') as file:
#         lines = file.readlines()
# 
#     with open(output_path, 'w', encoding='utf-8') as file:
#         for line in lines:
#             original_line = line.strip()
# 
#             # Inject translated names sequentially
#             for original_text, translated_text, original_name, translated_name in translation_pairs:
#                 if f'name={original_name}' in original_line:
#                     original_line = original_line.replace(f'name={original_name}', f'name={translated_name}')
# 
#             # Inject translated texts sequentially, handling line breaks
#             for original_text, translated_text, _, _ in translation_pairs:
#                 if f'text={original_text}' in original_line:
#                     if '\n' in translated_text:  # If translated text contains line breaks
#                         translated_text_lines = translated_text.split('\n')
#                         original_line = original_line.replace(f'text={original_text}', f'text={translated_text_lines[0]}')
#                         for additional_line in translated_text_lines[1:]:
#                             file.write(additional_line + '\n')
#                     else:
#                         original_line = original_line.replace(f'text={original_text}', f'text={translated_text}')
# 
#             # Ensure that choice texts are not overwritten
#             if '[choice' in original_line:
#                 for original_text, translated_text, _, _ in translation_pairs:
#                     if f'choice text={original_text}' in original_line:
#                         original_line = original_line.replace(f'choice text={original_text}', f'choice text={translated_text}')
# 
#             file.write(original_line + '\n')

import pandas as pd
import re

def inject_translations(txt_path, xlsx_path, output_path):
    # Read the Excel file
    df = pd.read_excel(xlsx_path)

    # Ensure 'translated text' and 'translated name' columns are treated as strings
    df['translated text'] = df['translated text'].astype(str)
    df['translated name'] = df['translated name'].astype(str)

    # Replace line breaks in the translated text with '\\n'
    df['translated text'] = df['translated text'].apply(lambda x: x.replace('\n', '\\n'))

    # Create iterators for translated texts and names
    translated_texts_iter = iter(df['translated text'])
    translated_names_iter = iter(df['translated name'])

    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(output_path, 'w', encoding='utf-8') as file:
        for line in lines:
            original_line = line.strip()

            # Inject translated names sequentially
            if 'name=' in original_line:
                try:
                    translated_name = next(translated_names_iter)
                    original_line = re.sub(r'name=[^ ]+', f'name={translated_name}', original_line)
                except StopIteration:
                    pass

            # Inject translated texts sequentially
            if 'text=' in original_line:
                try:
                    translated_text = next(translated_texts_iter)
                    original_line = re.sub(r'text=[^ ]+', f'text={translated_text}', original_line)
                except StopIteration:
                    pass

            # Ensure that choice texts are handled correctly
            if '[choice' in original_line:
                choice_matches = re.findall(r'choice text=[^\]]+', original_line)
                for choice_match in choice_matches:
                    try:
                        translated_choice_text = next(translated_texts_iter)
                        # Ensure the choice text is wrapped correctly
                        original_line = original_line.replace(choice_match, f'choice text="{translated_choice_text}"')
                    except StopIteration:
                        pass

            file.write(original_line + '\n')