from typing import Iterator
from data_types import TranslationLine
from commu_parser import CommuGroup, StringProperty
from spreadsheet import get_tl_lines_from_spreadsheet


def inject_tl_line(group: CommuGroup, tl_lines_iterator: Iterator[TranslationLine]):
    group_type = group.group_type

    if group_type == "choicegroup":
        # A choicegroup contains multiple "choices" properties
        # We inject tl_lines into each "choices" group
        for subgroup in group.get_property_list("choices"):
            inject_tl_line(subgroup, tl_lines_iterator)
        return

    if not (
        group_type == "message" or group_type == "narration" or group_type == "choice"
    ):
        return

    tl_line = tl_lines_iterator.__next__()
    if tl_line.group_type != group_type:
        raise Exception("Group type does not match")
    if tl_line.name != group.get_property("name", ""):
        raise Exception("Raw name property does not match")
    if tl_line.text != group.get_property("text", ""):
        raise Exception("Raw text does not match")

    group.modify_property("name", StringProperty(tl_line.translated_name))
    group.modify_property("text", StringProperty(tl_line.translated_text))


def inject_translations(txt_path, xlsx_path, output_path):
    # Read lines from the spreadsheet
    tl_lines = get_tl_lines_from_spreadsheet(xlsx_path, "Sheet1")

    # Read commu groups from the text file
    with open(txt_path, "r", encoding="utf-8") as file:
        groups = [CommuGroup.from_commu_line(line) for line in file]

    # Inject translations into the commu groups
    # We want to remember our position in the list of translated lines
    # as we inject in the commu groups, so we get an iterator
    # and use the same iterator for all injections
    tl_lines_iterator = tl_lines.__iter__()
    for group in groups:
        inject_tl_line(group, tl_lines_iterator)

    # Write the modified commu groups to the output file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join([str(group) for group in groups]))
