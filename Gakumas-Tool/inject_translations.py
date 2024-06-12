 # Original version
 # It works, but for some reason, original .txt lines that contain line breaks wont be injected with translated lines.

 import pandas as pd
 
 def inject_translations(txt_path, xlsx_path, output_path):
     # Read the Excel file
     df = pd.read_excel(xlsx_path)
 
     # Ensure 'text', 'translated text', 'name', and 'translated name' columns are treated as strings
     df['text'] = df['text'].astype(str)
     df['translated text'] = df['translated text'].astype(str)
     df['name'] = df['name'].astype(str)
     df['translated name'] = df['translated name'].astype(str)
 
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
 
             # Inject translated texts sequentially, handling line breaks
             for original_text, translated_text, _, _ in translation_pairs:
                 if f'text={original_text}' in original_line:
                     if '\n' in translated_text:  # If translated text contains line breaks
                         translated_text_lines = translated_text.split('\n')
                         original_line = original_line.replace(f'text={original_text}', f'text={translated_text_lines[0]}')
                         for additional_line in translated_text_lines[1:]:
                             file.write(additional_line + '\n')
                     else:
                         original_line = original_line.replace(f'text={original_text}', f'text={translated_text}')
 
             # Ensure that choice texts are not overwritten
             if '[choice' in original_line:
                 for original_text, translated_text, _, _ in translation_pairs:
                     if f'choice text={original_text}' in original_line:
                         original_line = original_line.replace(f'choice text={original_text}', f'choice text={translated_text}')
 
             file.write(original_line + '\n')

# Experimental version
#
#import pandas as pd
#import re
#
#def preprocess_translations(df):
#    # Replace line breaks in the translated text with '\n'
#    df['translated text'] = df['translated text'].str.replace('\n', '\\n')
#    df['translated name'] = df['translated name'].str.replace('\n', '\\n')
#    return df
#
#def preprocess_line(line):
#    # Replace line breaks with '\\n'
#    return line.replace('\n', '\\n')
#
#def inject_translations(txt_path, xlsx_path, output_path):
#    # Read the Excel file
#    df = pd.read_excel(xlsx_path)
#
#    # Preprocess translations to handle line breaks
#    df = preprocess_translations(df)
#
#    # Create iterators for translated texts and names
#    translated_texts_iter = iter(df['translated text'])
#    translated_names = df['translated name'].tolist()  # Get the list of translated names
#
#    with open(txt_path, 'r', encoding='utf-8') as file:
#        lines = file.readlines()
#
#    with open(output_path, 'w', encoding='utf-8') as file:
#        choice_text_index = 0  # Index for tracking translated choice texts
#        current_choice_group = None  # Track the current choice group being processed
#        for line in lines:
#            original_line = line.strip()
#
#            # Preprocess the line
#            original_line = preprocess_line(original_line)
#
#            # Inject translated texts sequentially
#            if 'text=' in original_line:
#                try:
#                    translated_text = next(translated_texts_iter)
#                    original_line = re.sub(r'text=[^ ]+', f'text={translated_text}', original_line)
#                except StopIteration:
#                    pass
#
#            # Ensure that choice texts are handled correctly
#            if '[choice' in original_line:
#                # Check if this line belongs to a new choice group
#                if 'choices=[' in original_line:
#                    current_choice_group = original_line
#                    choice_text_index = 0  # Reset the choice text index for the new group
#                else:
#                    try:
#                        translated_choice_text = next(translated_texts_iter)
#                        # Replace the choice text in the current choice group
#                        original_line = current_choice_group.replace(f'choices=[', f'choices=[choice text="{translated_choice_text}" ')
#                        choice_text_index += 1
#                    except StopIteration:
#                        pass
#
#            # Inject translated names if the line contains 'name='
#            if 'name=' in original_line:
#                try:
#                    translated_name = translated_names.pop(0)
#                    original_line = re.sub(r'name=[^ ]+', f'name={translated_name}', original_line)
#                except IndexError:
#                    pass
#
#            # Replace '\\n' with '\n' (for compatibility with escape sequences)
#            original_line = original_line.replace('\\n', '\n')
#
#            file.write(original_line + '\n')