from commu_parser import CommuGroup
from data_types import RawLine

# Fields that need translating:
# message.text, narration.text, choice.text, message.name
# Fields that might need translating:
# overwritecharactersetting.name, title.title


def create_raw_data_rows(group: CommuGroup) -> list[RawLine]:
    group_type = group.group_type

    if group_type == "choicegroup":
        # A choicegroup contains multiple 'choices' properties
        # We create a data row from each 'choices' property
        return [
            raw_line
            for subgroup in group.get_property_list("choices")
            for raw_line in create_raw_data_rows(subgroup)
        ]

    if not (
        group_type == "message" or group_type == "narration" or group_type == "choice"
    ):
        return []

    name = group.get_property("name", "")
    text = group.get_property("text", "")
    return [RawLine(group_type=group_type, name=name, text=text)]


def extract_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [
            raw_line
            for line in file
            for raw_line in create_raw_data_rows(CommuGroup.from_commu_line(line))
        ]
