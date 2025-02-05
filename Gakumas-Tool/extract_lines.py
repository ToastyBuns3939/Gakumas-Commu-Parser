from commu_parser import CommuGroup
from data_types import RawLine


def create_raw_data_rows(group: CommuGroup) -> list[RawLine]:
    group_type = group.group_type
    group_name = group.get_property("name", "")
    group_text = group.get_property("text", "")
    if not (group_name == "" and group_text == ""):
        raw_data_rows = [
            RawLine(group_type=group_type, name=group_name, text=group_text)
        ]
    else:
        raw_data_rows = []
    raw_data_rows.extend(
        raw_line
        for child_group in group.get_children()
        for raw_line in create_raw_data_rows(child_group)
    )
    return raw_data_rows


def extract_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [
            raw_line
            for line in file
            for raw_line in create_raw_data_rows(CommuGroup.from_commu_line(line))
        ]
