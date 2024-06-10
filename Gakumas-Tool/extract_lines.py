import re

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

            if line_type == 'choice':
                # Extract choice texts from the choicegroup
                choice_texts = re.findall(r'choice text=(.*?)(?:\sname=|\s?\]|\[|$)', line)
                for choice_text in choice_texts:
                    names.append('')
                    texts.append(choice_text.strip())
                    types.append('choice')
            else:
                # Extract text and name fields
                text_match = re.search(r'(?:message|narration) text=(.*?)(?:\sname=|\s?\]|\[|$)', line)
                name_match = re.search(r'name=(.*?)(?:\s|\]|$)', line)

                if text_match:
                    jp_text = text_match.group(1).strip()
                    if not name_match:
                        names.append('')  # Append empty string if no name field found
                    else:
                        names.append(name_match.group(1).strip())
                    texts.append(jp_text)
                    types.append(line_type)

    # Skip files without valid lines for extraction
    if not (message_text_found or narration_text_found or choice_text_found):
        return None, None, None, False, False, False

    return names, texts, types, message_text_found, narration_text_found, choice_text_found