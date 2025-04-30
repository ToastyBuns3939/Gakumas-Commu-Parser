import openpyxl
import re
import os
import sys # Import the sys module to access command-line arguments

def modify_excel_column_forward(input_filepath, output_filepath):
    """
    Modifies cells in the 'translated text' column of an Excel file
    based on specific character replacement rules (converting to ――),
    preserves original formatting.

    Args:
        input_filepath (str): The path to the input Excel file.
        output_filepath (str): The path where the modified Excel file will be saved.
    """
    try:
        # Load the workbook
        workbook = openpyxl.load_workbook(input_filepath)
        sheet = workbook.active # Work on the active sheet

        # Find the column index for 'translated text'
        header_row = sheet[1] # Assuming header is in the first row
        translated_text_col_index = -1
        for col_index, cell in enumerate(header_row):
            # Use strip().lower() for case-insensitive and whitespace-agnostic matching
            if isinstance(cell.value, str) and cell.value.strip().lower() == 'translated text':
                translated_text_col_index = col_index + 1 # openpyxl is 1-indexed for columns
                break

        if translated_text_col_index == -1:
            print(f"Warning: 'translated text' column not found in '{os.path.basename(input_filepath)}'. Skipping this file.")
            return

        # Iterate through rows, starting from the second row (index 2 in openpyxl)
        # to skip the header.
        for row_index in range(2, sheet.max_row + 1):
            cell = sheet.cell(row=row_index, column=translated_text_col_index)
            cell_value = cell.value

            # Check if the cell value is a string before attempting replacements
            if isinstance(cell_value, str):
                modified_value = cell_value

                # --- Character Replacement Rules ---

                # Rule 1: Replace "…" with "..."
                modified_value = modified_value.replace("…", "...")

                # Rule 2: Replace "~" with "～"
                modified_value = modified_value.replace("~", "～")

                # Rule 3: Remove space before -, ー, or — (but NOT before ――).
                modified_value = re.sub(r'\s+([-ー—])', r'\1', modified_value)

                # Rule 4: Convert pre-existing double hyphens '--' to horizontal bar '――'.
                modified_value = modified_value.replace('--', '――')

                # Rule 5: Convert pre-existing double long dashes 'ーー' to horizontal bar '――'.
                modified_value = modified_value.replace('ーー', '――')

                # Rule 6: Convert pre-existing double em dashes '——' (U+2014 U+2014) to horizontal bar '――'.
                modified_value = modified_value.replace('——', '――')

                # Rule 7: Convert pre-existing box-drawing double hyphen '──' to horizontal bar '――'.
                modified_value = modified_value.replace('──', '――')

                # Rule 8: Convert a single -, ー, or — immediately following one or more ―― to ――.
                modified_value = re.sub(r'(――+)([-ー—])', r'\1――', modified_value)

                # --- Rule for single hyphens, long dashes, and em dashes ---
                # Convert to ―― ONLY if NOT strictly between two word characters.
                # Use a custom function to check surrounding characters explicitly.
                def convert_dash_unless_between_words(match):
                    # Get the matched dash character
                    dash = match.group(0)
                    # Get the index of the matched dash
                    start_index = match.start()
                    end_index = match.end()

                    # Get the character immediately before the dash (if it exists)
                    pre_char = modified_value[start_index - 1] if start_index > 0 else ''
                    # Get the character immediately after the dash (if it exists)
                    post_char = modified_value[end_index] if end_index < len(modified_value) else ''

                    # Check if BOTH the preceding and following characters are word characters (\w)
                    # Use re.match to check if the character is a word character
                    is_between_words = bool(re.match(r'\w', pre_char)) and bool(re.match(r'\w', post_char))

                    if is_between_words:
                        # If strictly between two word characters, keep the original dash
                        return dash
                    else:
                        # Otherwise, convert to ――
                        return '――'

                # Rule 9: Apply the conversion function to all single '-', 'ー', or '—'.
                # This regex matches any single hyphen, long dash, or em dash.
                modified_value = re.sub(r'([-ー—])', convert_dash_unless_between_words, modified_value)


                # Update the cell value. openpyxl preserves formatting when updating value.
                cell.value = modified_value


        # Save the modified workbook
        workbook.save(output_filepath)

        print(f"Successfully applied forward conversion to '{os.path.basename(input_filepath)}' and saved to '{os.path.basename(output_filepath)}'")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_filepath}' during processing.")
    except Exception as e:
        print(f"An error occurred while processing '{os.path.basename(input_filepath)}': {e}")


# --- How to use the script ---
if __name__ == "__main__":
    # Check if the correct number of command-line arguments are provided
    # sys.argv[0] is the script name itself
    # sys.argv[1] should be the input folder path
    # sys.argv[2] should be the output folder path
    if len(sys.argv) != 3:
        print("Usage: python your_script_name.py <input_folder_path> <output_folder_path>")
        sys.exit(1) # Exit with an error code

    # Get input and output folder paths from command-line arguments
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    # The action is now fixed to 'forward' since only that function remains
    action = 'forward'

    # Ensure output folder exists, create if necessary
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
            print(f"Created output folder: '{output_folder}'")
        except OSError as e:
            print(f"Error: Could not create output folder '{output_folder}': {e}")
            sys.exit(1) # Exit if output folder cannot be created

    # Check if the input folder exists before proceeding
    if not os.path.isdir(input_folder):
        print(f"Error: The input path '{input_folder}' is not a valid directory.")
        print("Please check the path and try again.")
        sys.exit(1) # Exit if input path is not a directory
    else:
        print(f"Processing Excel files in '{input_folder}' for {action} conversion...")
        # Iterate through all files in the input folder
        for filename in os.listdir(input_folder):
            # Construct the full input file path
            input_filepath = os.path.join(input_folder, filename)

            # Check if the item is a file and is an Excel file (xlsx format is best for openpyxl)
            if os.path.isfile(input_filepath) and filename.endswith('.xlsx'):
                # Construct the output file path using the original filename
                output_filepath = os.path.join(output_folder, filename)

                # Process the Excel file using the forward conversion function
                modify_excel_column_forward(input_filepath, output_filepath)


        print(f"\nBatch {action} conversion complete.")
