import openpyxl
import xlsxwriter
import os
from name_dictionary import name_translation_dict

def convert_to_string(data):
    if data is None:
        return ''
    else:
        return str(data)

def row_to_strings(data_row):
    return tuple(convert_to_string(a) for a in data_row)

def translate_name(name):
    # Translate names using the provided dictionary
    return name_translation_dict.get(name.strip(), '')

column_headers = ('type', 'name', 'translated name', 'text', 'translated text')
def save_to_excel(raw_data_rows, output_path, worksheet_name):
    existing_data_rows = []
    if os.path.exists(output_path):  # Check if output file already exists
        # Read data from workbook and check it has the right column headers
        workbook = openpyxl.load_workbook(filename=output_path)
        existing_data_rows = [
            row_to_strings(data_row)
            for data_row in workbook[worksheet_name].values]
        existing_column_headers = existing_data_rows[0]
        if existing_column_headers != column_headers:
            raise Exception("Existing spreadsheet has incorrect column headers")
        existing_data_rows = existing_data_rows[1:]

    # Don't do anything if the data from the commu files (raw_data_rows)
    # is the same as the data from the existing spreadsheet (existing_raw_data_rows)
    existing_raw_data_rows = [
        (data_row[0], data_row[1], data_row[3])
        for data_row in existing_data_rows
    ]
    if raw_data_rows == existing_raw_data_rows:
        return

    # Create a list of spreadsheet row data
    # We insert the existing translations if the original strings in
    # the type, name, text columns are all the same
    new_data_rows = []
    for raw_data_row in raw_data_rows:
        try:
            data_row = next(data_row
                for data_row in existing_data_rows
                if (data_row[0], data_row[1], data_row[3]) == raw_data_row)
            # Remove the matching row we found
            # This means that if for some reason there are two different rows
            # with the same original strings, the second one will be copied over
            # the second time (instead of the first one being copied over every time)
            existing_data_rows.remove(data_row)
        except StopIteration:
            data_row = (raw_data_row[0],
                        raw_data_row[1],
                        translate_name(raw_data_row[1]), # We can translate the name
                        raw_data_row[2],
                        '')
        new_data_rows.append(data_row)

    # Create the spreadsheet
    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet(worksheet_name)

    # Write data to the worksheet
    worksheet.write_row(0, 0, column_headers)
    for index, new_data_row in enumerate(new_data_rows):
        worksheet.write_row(index + 1, 0, new_data_row)
        # Adjust row heights automatically based on the content
        text_line_count = new_data_row[3].count('\n') + 1
        translated_text_line_count = new_data_row[4].count('\n') + 1
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