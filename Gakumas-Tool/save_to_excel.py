import openpyxl
import xlsxwriter
import os
from name_dictionary import name_translation_dict
from data_types import RawLine, TranslationLine

def convert_to_string(data):
    if data is None:
        return ''
    else:
        return str(data)

def row_to_translation_line(data_row) -> TranslationLine:
    return TranslationLine(*(convert_to_string(a) for a in data_row))

def to_raw_line(translation_line: TranslationLine):
    return RawLine(
        group_type = translation_line.group_type,
        name = translation_line.name,
        text = translation_line.text
    )

def to_translation_line(raw_line: RawLine):
    return TranslationLine(
        group_type = raw_line.group_type,
        name = raw_line.name,
        translated_name = translate_name(raw_line.name), # We can translate the name
        text = raw_line.text,
        translated_text = '')

def translate_name(name: str):
    # Translate names using the provided dictionary
    return name_translation_dict.get(name.strip(), '')

column_headers = ('type', 'name', 'translated name', 'text', 'translated text')
def save_to_excel(
        raw_lines: list[RawLine],
        output_path: str,
        worksheet_name: str):
    existing_tl_lines = []
    if os.path.exists(output_path):  # Check if output file already exists
        # Read data from workbook and check it has the right column headers
        workbook = openpyxl.load_workbook(filename=output_path)
        existing_rows = list(workbook[worksheet_name].values)
        existing_column_headers = existing_rows[0]
        if existing_column_headers != column_headers:
            raise Exception("Existing spreadsheet has incorrect column headers")
        existing_tl_lines = [
            row_to_translation_line(data_row)
            for data_row in existing_rows[1:]]

    # Don't do anything if the data from the commu files (raw_data_rows)
    # is the same as the data from the existing spreadsheet (existing_raw_data_rows)
    existing_raw_lines = [to_raw_line(tl_line) for tl_line in existing_tl_lines]
    if raw_lines == existing_raw_lines:
        return

    # Create a list of spreadsheet row data
    # We insert the existing translations if the original strings in
    # the type, name, text columns are all the same
    new_tl_lines: list[TranslationLine] = []
    for raw_line in raw_lines:
        try:
            tl_line = next(tl_line
                for tl_line in existing_tl_lines
                if to_raw_line(tl_line) == raw_line)
            # Remove the matching row we found
            # This means that if for some reason there are two different rows
            # with the same original strings, the second one will be copied over
            # the second time (instead of the first one being copied over every time)
            existing_tl_lines.remove(tl_line)
        except StopIteration: # if no matching row found
            tl_line = to_translation_line(raw_line)
        new_tl_lines.append(tl_line)

    # Create the spreadsheet
    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet(worksheet_name)

    # Write data to the worksheet
    worksheet.write_row(0, 0, column_headers)
    for index, tl_line in enumerate(new_tl_lines):
        worksheet.write_row(index + 1, 0, tl_line)
        # Adjust row heights automatically based on the content
        text_line_count = tl_line.text.count('\n') + 1
        translated_text_line_count = tl_line.translated_text.count('\n') + 1
        row_height = (15 # Assuming default row height is 15 units
                        * max(text_line_count, translated_text_line_count))
        worksheet.set_row(index + 1, row_height)

    # Define a format for cell alignment and text wrapping
    dialogue_format = workbook.add_format({'align': 'left', 'valign': 'top', 'text_wrap': True})
    name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

    # Set column widths
    worksheet.set_column('A:A', 15, name_format)  # type column
    worksheet.set_column('B:B', 15, name_format)  # name column
    worksheet.set_column('C:C', 15, name_format)  # translated name column
    worksheet.set_column('D:D', 70, dialogue_format)  # text column
    worksheet.set_column('E:E', 70, dialogue_format)  # translated column

    # Close the workbook to save the Excel file
    workbook.close()