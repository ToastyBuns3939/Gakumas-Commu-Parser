import openpyxl
import openpyxl.styles
from name_dictionary import name_translation_dict
from data_types import RawLine, TranslationLine


def convert_to_string(data):
    if data is None:
        return ""
    else:
        return str(data)


def row_to_translation_line(data_row) -> TranslationLine:
    return TranslationLine(*(convert_to_string(a) for a in data_row))


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


column_headers = ("type", "name", "translated name", "text", "translated text")


def get_tl_lines_from_spreadsheet(
    spreadsheet_path: str, worksheet_name: str
) -> list[TranslationLine]:
    try:
        # Read data from workbook
        workbook = openpyxl.load_workbook(filename=spreadsheet_path)
        existing_rows = list(workbook[worksheet_name].values)

        # check it has the right column headers
        existing_column_headers = existing_rows[0]
        if existing_column_headers != column_headers:
            raise Exception("Existing spreadsheet has incorrect column headers")

        return [row_to_translation_line(data_row) for data_row in existing_rows[1:]]
    except FileNotFoundError:
        return []


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


def write_to_spreadsheet(
    tl_lines: list[TranslationLine], output_path: str, worksheet_name: str
):
    # Create the spreadsheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = worksheet_name

    # Write data to the worksheet
    worksheet.append(column_headers)
    for index, tl_line in enumerate(tl_lines):
        worksheet.append(tl_line)
        # Adjust row heights automatically based on the content
        text_line_count = tl_line.text.count("\n") + 1
        translated_text_line_count = tl_line.translated_text.count("\n") + 1
        row_height = 15 * max(  # Assuming default row height is 15 units
            text_line_count, translated_text_line_count
        )
        worksheet.row_dimensions[index + 2].height = row_height

    # Set column widths
    worksheet.column_dimensions["A"].width = 15  # type column
    worksheet.column_dimensions["B"].width = 15  # name column
    worksheet.column_dimensions["C"].width = 15  # translated name column
    worksheet.column_dimensions["D"].width = 40  # text column
    worksheet.column_dimensions["E"].width = 40  # translated column

    # Define formats for cell alignment and text wrapping
    dialogue_alignment = openpyxl.styles.Alignment(
        horizontal="left",
        vertical="top",
        # Excel doesn't display multiple lines unless the
        # cell has text wrapping
        # wrap_text = True
        # However Google Sheets does display multiple lines fine
        # without text wrapping, which is preferrable
    )
    name_alignment = openpyxl.styles.Alignment(horizontal="center", vertical="center")
    # Apply alignment formats
    for row in worksheet["A:C"]:
        for cell in row:
            cell.alignment = name_alignment
    for row in worksheet["D:E"]:
        for cell in row:
            cell.alignment = dialogue_alignment

    # Close the workbook to save the Excel file
    workbook.save(output_path)


def save_to_excel(raw_lines: list[RawLine], output_path: str, worksheet_name: str):
    existing_tl_lines = get_tl_lines_from_spreadsheet(output_path, worksheet_name)

    # Don't do anything if the raw data from the commu files
    # is the same as the raw data from the existing spreadsheet
    existing_raw_lines = [to_raw_line(tl_line) for tl_line in existing_tl_lines]
    if raw_lines == existing_raw_lines:
        return

    merged_tl_lines = merge_lines(raw_lines, existing_tl_lines)
    write_to_spreadsheet(merged_tl_lines, output_path, worksheet_name)
