import openpyxl
import re
import os

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

                # Rule 3: Remove space before -, ー, —, or ――
                modified_value = re.sub(r'\s+([-ー—――])', r'\1', modified_value)

                # Rule 4: Convert pre-existing double hyphens '--' to horizontal bar '――'.
                modified_value = modified_value.replace('--', '――')

                # Rule 5: Convert pre-existing double long dashes 'ーー' to horizontal bar '――'.
                modified_value = modified_value.replace('ーー', '――')

                # Rule 6: Convert pre-existing double em dashes '——' (U+2014 U+2014) to horizontal bar '――'.
                modified_value = modified_value.replace('——', '――')

                # Rule 7: Convert pre-existing box-drawing double hyphen '──' to horizontal bar '――'.
                modified_value = modified_value.replace('──', '――')

                # --- Rule for single hyphens, long dashes, and em dashes ---
                # Convert to ―― ONLY if NOT between two word characters.
                # This uses a regex that matches the dash and its potential surrounding word characters,
                # and a function to decide the replacement based on the match.
                def convert_dash_based_on_surroundings(match):
                    # match.groups() will return a tuple of captured groups (pre_char, dash, post_char)
                    # None if the optional group didn't match (start/end of string)
                    pre_char, dash, post_char = match.groups()

                    # Check if BOTH the preceding and following characters are word characters.
                    # If both are not None (meaning they were captured) AND are word characters.
                    is_between_words = (pre_char is not None and re.match(r'\w', pre_char)) and \
                                       (post_char is not None and re.match(r'\w', post_char))

                    if is_between_words:
                        # If between two word characters, keep the original dash
                        return dash
                    else:
                        # Otherwise, convert to ――
                        return '――'

                # Rule 8: Apply the conversion function to all single '-', 'ー', or '—'.
                # The regex matches an optional word character, followed by one of the dashes,
                # followed by an optional word character.
                modified_value = re.sub(r'(\w)?([-ー—])(\w)?', convert_dash_based_on_surroundings, modified_value)


                # Update the cell value. openpyxl preserves formatting when updating value.
                cell.value = modified_value


        # Save the modified workbook
        workbook.save(output_filepath)

        print(f"Successfully applied forward conversion to '{os.path.basename(input_filepath)}' and saved to '{os.path.basename(output_filepath)}'")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_filepath}' during processing.")
    except Exception as e:
        print(f"An error occurred while processing '{os.path.basename(input_filepath)}': {e}")


def modify_excel_column_reverse_specific(input_filepath, output_filepath):
    """
    Converts ―― back to - specifically when it appears between two sequences of non-whitespace characters.
    Preserves original formatting.

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

                # --- Character Replacement Rule (Specific Reverse) ---

                # Removed debug print: Show the value before the reverse conversion
                # print(f"DEBUG Reverse: Before Rule R1 (―― to - between non-whitespace) in row {row_index}: '{modified_value}'")

                # Removed debug print: Test the regex match
                # matches = re.findall(r'(\S+)――(\S+)', modified_value)
                # print(f"DEBUG Reverse: Regex matches found in row {row_index}: {matches}")


                # Rule R1: Convert ―― back to - ONLY when it appears between two sequences of non-whitespace characters.
                # Regex explanation:
                # (\S+)   : Captures one or more non-whitespace characters (Group 1)
                # ――      : Matches the horizontal bar character
                # (\S+)   : Captures one or more non-whitespace characters (Group 2)
                # Replacement r'\1-\2' puts the first captured sequence, a hyphen, and the second captured sequence back.
                modified_value = re.sub(r'(\S+)――(\S+)', r'\1-\2', modified_value)

                # Removed debug print: Show the value after the reverse conversion
                # print(f"DEBUG Reverse: After Rule R1 in row {row_index}: '{modified_value}'")


                # Update the cell value. openpyxl preserves formatting when updating value.
                cell.value = modified_value

        # Save the modified workbook
        workbook.save(output_filepath)

        print(f"Successfully applied specific reverse conversion to '{os.path.basename(input_filepath)}' and saved to '{os.path.basename(output_filepath)}'")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_filepath}' during processing.")
    except Exception as e:
        print(f"An error occurred while processing '{os.path.basename(input_filepath)}': {e}")


# --- How to use the script ---
if __name__ == "__main__":
    # Prompt the user for the action using numbers
    print("Select action:")
    print("1. Forward conversion (convert to ――)")
    print("2. Specific reverse conversion (convert ―― to - between non-whitespace characters)")
    action_choice = input("Enter the number for the desired action: ")

    # Map the number choice to the action string
    if action_choice == '1':
        action = 'forward'
    elif action_choice == '2':
        action = 'reverse_specific'
    else:
        print("Invalid choice. Please enter 1 or 2.")
        exit() # Exit if the choice is invalid

    # Prompt the user for input and output folder paths
    input_folder = input(f"Enter the path to the input folder containing Excel files for {action} conversion: ")
    output_folder = input(f"Enter the path for the output folder to save modified files after {action} conversion: ")

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
        print(f"Processing Excel files in '{input_folder}' for {action} conversion...")
        # Iterate through all files in the input folder
        for filename in os.listdir(input_folder):
            # Construct the full input file path
            input_filepath = os.path.join(input_folder, filename)

            # Check if the item is a file and is an Excel file (xlsx format is best for openpyxl)
            if os.path.isfile(input_filepath) and filename.endswith('.xlsx'):
                # Construct the output file path using the original filename
                output_filepath = os.path.join(output_folder, filename)

                # Process the Excel file based on the chosen action
                if action == 'forward':
                    modify_excel_column_forward(input_filepath, output_filepath)
                elif action == 'reverse_specific':
                    modify_excel_column_reverse_specific(input_filepath, output_filepath)

                elif os.path.isfile(input_filepath):
                     print(f"Skipping non-xlsx or non-file item: '{filename}'")


            print(f"\nBatch {action} conversion complete.")
