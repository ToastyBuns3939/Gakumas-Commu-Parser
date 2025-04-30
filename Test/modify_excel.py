import openpyxl
import re
import os

def modify_excel_column_with_formatting(input_filepath, output_filepath):
    """
    Modifies cells in the 'translated text' column of an Excel file
    based on specific character replacement rules, preserving original formatting.

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

                # Print original value for debugging
                # print(f"DEBUG: Original value in row {row_index}: '{cell_value}'")

                # Rule 1: Replace "…" with "..."
                modified_value = modified_value.replace("…", "...")
                # print(f"DEBUG: After Rule 1 (...): '{modified_value}'")


                # Rule 2: Replace "~" with "～"
                modified_value = modified_value.replace("~", "～")
                # print(f"DEBUG: After Rule 2 (～): '{modified_value}'")


                # Rule 3: Remove space before -, ー, —, or ─
                # Added Em Dash '—' to the characters to check for leading space
                modified_value = re.sub(r'\s+([-ー—─])', r'\1', modified_value)
                # print(f"DEBUG: After Rule 3 (Remove Space): '{modified_value}'")

                # Print value before double hyphen/dash conversion for debugging
                print(f"DEBUG: Before Rule 4/5/6/7 (--/ーー/――/—— to ──) in row {row_index}: '{modified_value}'")

                # Rule 4: Convert pre-existing double hyphens '--' to box-drawing double hyphen '──'.
                modified_value = modified_value.replace('--', '──')
                # print(f"DEBUG: After Rule 4 (-- to ──): '{modified_value}'")

                # Rule 5: Convert pre-existing double long dashes 'ーー' to box-drawing double hyphen '──'.
                modified_value = modified_value.replace('ーー', '──')
                # print(f"DEBUG: After Rule 5 (ーー to ──): '{modified_value}'")

                # Rule 6: Convert pre-existing horizontal bar '――' (U+2015) to box-drawing double hyphen '──'.
                modified_value = modified_value.replace('――', '──')
                # print(f"DEBUG: After Rule 6 (―― to ──): '{modified_value}'")

                # Rule 7: Convert pre-existing double em dashes '——' (U+2014 U+2014) to box-drawing double hyphen '──'.
                modified_value = modified_value.replace('——', '──')
                # Print value after double hyphen/dash conversion for debugging
                print(f"DEBUG: After Rule 4/5/6/7 (--/ーー/――/—— to ──) in row {row_index}: '{modified_value}'")


                # --- Rules for single hyphens and long dashes (convert to ── if not between words) ---
                # Apply rules for specific "open" cases first.

                # Rule 8: Convert single '-', 'ー', or '—' at the end of a word to '──'.
                # Matches a dash/hyphen preceded by a word character (\w) and not followed by a word character (?!w).
                modified_value = re.sub(r'(?<=\w)([-ー—])(?!\w)', r'──', modified_value)
                # print(f"DEBUG: After Rule 8 (word- to word──): '{modified_value}'")

                # Rule 9: Convert single '-', 'ー', or '—' at the start of a word to '──'.
                # Matches a dash/hyphen not preceded by a word character (?<!w) and followed by a word character (?=w).
                modified_value = re.sub(r'(?<!\w)([-ー—])(?=\w)', r'──', modified_value)
                # print(f"DEBUG: After Rule 9 (-word to ──word): '{modified_value}'")

                # Rule 10: Convert isolated single '-', 'ー', or '—' (not adjacent to word characters) to '──'.
                # Matches a dash/hyphen not preceded by a word character (?<!w) and not followed by a word character (?!w).
                modified_value = re.sub(r'(?<!\w)([-ー—])(?!\w)', r'──', modified_value)
                # print(f"DEBUG: After Rule 10 (isolated -/ー/— to ──): '{modified_value}'")


                # Rule 11: If a cell contains ONLY a single "─", turn it into "──".
                # This is a specific case to ensure a lonely ─ is doubled,
                # acting as a final catch after other rules.
                if modified_value == "─":
                    modified_value = "──"
                    # print(f"DEBUG: After Rule 11 (Cell is only ─): '{modified_value}'")


                # Update the cell value. openpyxl preserves formatting when updating value.
                cell.value = modified_value

        # Save the modified workbook
        workbook.save(output_filepath)

        print(f"Successfully modified '{os.path.basename(input_filepath)}' and saved to '{os.path.basename(output_filepath)}'")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_filepath}' during processing.")
    except Exception as e:
        print(f"An error occurred while processing '{os.path.basename(input_filepath)}': {e}")

# --- How to use the script ---
if __name__ == "__main__":
    # Prompt the user for input and output folder paths
    input_folder = input("Enter the path to the input folder containing Excel files: ")
    output_folder = input("Enter the path for the output folder to save modified files: ")

    # Ensure output folder exists, create if necessary
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
            print(f"Created output folder: '{output_folder}'")
        except OSError as e:
            print(f"Error: Could not create output folder '{output_folder}': {e}")
            exit() # Exit if output folder cannot be created

    # Check if the input folder exists before proceeding
    if not os.path.isdir(input_folder):
        print(f"Error: The input path '{input_folder}' is not a valid directory.")
        print("Please check the path and try again.")
    else:
        print(f"Processing Excel files in '{input_folder}'...")
        # Iterate through all files in the input folder
        for filename in os.listdir(input_folder):
            # Construct the full input file path
            input_filepath = os.path.join(input_folder, filename)

            # Check if the item is a file and is an Excel file (xlsx format is best for openpyxl)
            if os.path.isfile(input_filepath) and filename.endswith('.xlsx'):
                # Construct the output file path using the original filename
                output_filepath = os.path.join(output_folder, filename)

                # Process the Excel file
                modify_excel_column_with_formatting(input_filepath, output_filepath)
            elif os.path.isfile(input_filepath):
                 print(f"Skipping non-xlsx or non-file item: '{filename}'")


        print("\nBatch processing complete.")
