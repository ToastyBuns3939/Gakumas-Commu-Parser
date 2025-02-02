from typing import Iterator
from data_types import TranslationLine
from commu_parser import CommuGroup
from spreadsheet import get_tl_lines_from_spreadsheet


def inject_tl_line(
    group: CommuGroup,
    group_line_number: int,
    tl_lines_iterator: enumerate[TranslationLine],
):
    group_type = group.group_type

    if group_type == "choicegroup":
        # A choicegroup contains multiple "choices" properties
        # We inject tl_lines into each "choices" group
        for subgroup in group.get_property_list("choices"):
            inject_tl_line(subgroup, group_line_number, tl_lines_iterator)
        return

    if not (
        group_type == "message" or group_type == "narration" or group_type == "choice"
    ):
        return

    group_name = group.get_property("name", "")
    group_text = group.get_property("text", "")
    if group_name == "" and group_text == "":
        return

    try:
        tl_line_index, tl_line = tl_lines_iterator.__next__()
    except StopIteration:
        raise Exception(
            f"Spreadsheet has too few lines!"
            + f"No row in spreadsheet matching commu line {group_line_number}"
        )
    if tl_line.group_type != group_type:
        raise Exception(
            f"Group type does not match! "
            + f"Commu file line {group_line_number} has group type\n{group_type}\n"
            + f"but spreadsheet row {tl_line_index + 2} "
            + f"has group type\n{tl_line.group_type}"
        )
    if tl_line.name != group_name:
        raise Exception(
            f"Raw name does not match! "
            + f"Commu file line {group_line_number} has raw name\n{group_name}\n"
            + f"but spreadsheet row {tl_line_index + 2} "
            + f"has raw name\n{tl_line.name}"
        )
    if tl_line.text != group_text:
        raise Exception(
            f"Raw text does not match! "
            + f"Commu file line {group_line_number} has raw text\n{group_text}\n"
            + f"but spreadsheet row {tl_line_index + 2} "
            + f"has raw text\n{tl_line.text}"
        )

    translated_name = (
        tl_line.translated_name if tl_line.translated_name != "" else tl_line.name
    )
    translated_text = (
        tl_line.translated_text if tl_line.translated_text != "" else tl_line.text
    )
    group.modify_property("name", translated_name)
    group.modify_property("text", translated_text)


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
    tl_lines_iterator = enumerate(tl_lines).__iter__()
    for index, group in enumerate(groups):
        inject_tl_line(group, index + 1, tl_lines_iterator)

    # Write the modified commu groups to the output file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join([str(group) for group in groups]))
        file.write("\n")
