import re

def parse_group_type(text_to_parse):
    match = re.match(r'([a-z]+)[ \]]', text_to_parse) # Note: re.match searches from the start of the string
    if not match:
        raise Exception()
    return match.group(1), text_to_parse[match.end(1):]

# This function gobbles up the = as well!
def parse_key(text_to_parse):
    match = re.match(r'([A-Za-z]+)=', text_to_parse)
    if not match:
        raise Exception()
    return match.group(1), text_to_parse[match.end():]

def parse_string_data(text_to_parse):
    match = re.match(r'((?:[^\n\\\[\]=]|\\n|\\=)+)[ \]]', text_to_parse)
    # The first match-group consists of any character except
    # linebreak, backslash, square brackets, and equals, unless they are
    # in the combinations '\n' or '\='
    if not match:
        raise Exception()
    return match.group(1), text_to_parse[match.end(1):]

def parse_json_data(text_to_parse):
    match = re.match(r'(\\\{\S+\\\})([ \]])', text_to_parse)
    if not match:
        raise Exception()
    return match.group(1), text_to_parse[match.end(1):]

def parse_animation_curve_json_data(text_to_parse):
    match = re.match(r'(AnimationCurve::\\\{\S+\\\})([ \]])', text_to_parse)
    if not match:
        raise Exception()
    return match.group(1), text_to_parse[match.end(1):]

def parse_group(text_to_parse):
    if text_to_parse[0] != '[':
        raise Exception()
    group_type, text_to_parse = parse_group_type(text_to_parse[1:])
    group = {'group_type': group_type, 'property_pairs': []}
    while text_to_parse[0] != ']':
        if text_to_parse[0] != ' ':
            raise Exception()
        text_to_parse = text_to_parse[1:]
        key, text_to_parse = parse_key(text_to_parse)
        if re.match(r'\[', text_to_parse):
            data, text_to_parse = parse_group(text_to_parse)
        elif re.match(r'AnimationCurve::\\\{', text_to_parse):
            data, text_to_parse = parse_animation_curve_json_data(text_to_parse)
        elif re.match(r'\\\{', text_to_parse):
            data, text_to_parse = parse_json_data(text_to_parse)
        else:
            data, text_to_parse = parse_string_data(text_to_parse)
        group['property_pairs'].append((key, data))
    return group, text_to_parse[1:]