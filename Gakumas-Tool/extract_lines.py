from commu_parser import CommuGroup

# Fields that need translating:
# message.text, narration.text, choice.text, message.name
# Fields that might need translating:
# overwritecharactersetting.name, title.title

def create_raw_data_rows(group: CommuGroup):
    group_type = group.group_type
    
    if group_type == 'choicegroup':
        # A choicegroup contains multiple 'choices' properties
        # We create a data row from each 'choices' property 
        return [
            raw_data_row
            for subgroup in group.get_property_list('choices')
                for raw_data_row in create_raw_data_rows(subgroup)]
    
    if not (group_type == 'message' or group_type == 'narration' or group_type == 'choice'):
        return []

    name = group.get_property('name', '')
    text = group.get_property('text', '')
    return [(group_type, name, text)]

def extract_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [
            raw_data_row
            for line in file
                for raw_data_row in create_raw_data_rows(CommuGroup.from_commu_line(line))]
