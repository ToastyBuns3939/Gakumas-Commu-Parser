from commu_parser import parse_commu_line

# Fields that need translating:
# message.text, narration.text, choice.text, message.name
# Fields that might need translating:
# overwritecharactersetting.name, title.title

def getProperty(group, key, defaultValue):
    found_properties = [pair[1] for pair in group['property_pairs'] if pair[0] == key]
    if len(found_properties) == 1:
        return found_properties[0]
    elif len(found_properties) == 0:
        return defaultValue
    else:
        raise Exception(f"More than one property with key '{key}' found in group!")

def create_raw_data_rows(group):
    group_type = group['group_type']
    
    if group_type == 'choicegroup':
        # A choicegroup contains multiple 'choices' properties
        # We create a data row from each 'choices' property 
        return [
            raw_data_row
            for subgroup_pair in group['property_pairs']
                if subgroup_pair[0] == 'choices'
                    for raw_data_row in create_raw_data_rows(subgroup_pair[1])]
    
    if not (group_type == 'message' or group_type == 'narration' or group_type == 'choice'):
        return []

    name = getProperty(group, 'name', '')
    text = getProperty(group, 'text', '')
    return [(group_type, name, text)]

def extract_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [
            raw_data_row
            for line in file
                for raw_data_row in create_raw_data_rows(parse_commu_line(line))]
