from name_dictionary import name_translation_dict
from data_types import RawLine, TranslationLine
from spreadsheet import get_tl_lines_from_spreadsheet, write_tl_lines_to_spreadsheet


def to_raw_line(translation_line: TranslationLine):
    return RawLine(
        group_type=translation_line.group_type,
        name=translation_line.name,
        text=translation_line.text,
    )


def to_translation_line(raw_line: RawLine):
    return TranslationLine(
        group_type=raw_line.group_type,
        name=raw_line.name,
        translated_name=translate_name(raw_line.name),  # We can translate the name
        text=raw_line.text,
        translated_text="",
    )


def translate_name(name: str):
    # Translate names using the provided dictionary
    return name_translation_dict.get(name.strip(), "")


def merge_lines(raw_lines: list[RawLine], existing_tl_lines: list[TranslationLine]):
    new_tl_lines: list[TranslationLine] = []
    # We insert the existing translations if the original strings in
    # the type, name, text columns are all the same
    for raw_line in raw_lines:
        try:
            tl_line = next(
                tl_line
                for tl_line in existing_tl_lines
                if to_raw_line(tl_line) == raw_line
            )
            # Remove the matching row we found
            # This means that if for some reason there are two different rows
            # with the same original strings, the second one will be copied over
            # the second time (instead of the first one being copied over every time)
            existing_tl_lines.remove(tl_line)
        except StopIteration:  # if no matching row found
            tl_line = to_translation_line(raw_line)
        new_tl_lines.append(tl_line)
    return new_tl_lines


def save_to_excel(
    raw_lines: list[RawLine],
    output_path: str,
    worksheet_name: str,
    force_overwrite: bool,
):
    try:
        existing_tl_lines = get_tl_lines_from_spreadsheet(output_path, worksheet_name)
    except FileNotFoundError:
        existing_tl_lines = []

    # Don't do anything if the raw data from the commu files
    # is the same as the raw data from the existing spreadsheet
    # and we aren't force overwriting
    existing_raw_lines = [to_raw_line(tl_line) for tl_line in existing_tl_lines]
    if not force_overwrite and raw_lines == existing_raw_lines:
        print(f"No change in raw lines in {output_path}, skipping...")
        return

    merged_tl_lines = merge_lines(raw_lines, existing_tl_lines)
    write_tl_lines_to_spreadsheet(merged_tl_lines, output_path, worksheet_name)
    print(f"Conversion completed for {output_path}")
