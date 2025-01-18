import os
import sys
import argparse
import tkinter as tk
from tkinter import filedialog
from extract_lines import extract_lines
from save_to_excel import save_to_excel
from inject_translations import inject_translations

def create_argument_parser():
    parser = argparse.ArgumentParser(
        prog = 'Gakumas Commu Parser',
        description = 'Gakuen Idolm@ster commu text conversion tool'
    )
    subparsers = parser.add_subparsers()
    parser_extract = subparsers.add_parser(
        'extract',
        help = 'Extracts strings from commu txt files in txt_directory ' +
            'and generates spreadsheet files in xlsx_directory')
    parser_extract.add_argument('txt_directory',
                                help = 'The directory containing the commu txt files')
    parser_extract.add_argument('xlsx_directory',
                                help = 'The directory to hold the spreadsheets')
    parser_extract.set_defaults(func = generate_xlsx_files)
    parser_inject = subparsers.add_parser(
        'inject',
        help = 'Injects strings from spreadsheets in xlsx_directory ' +
            'into the commu files from in_txt_directory ' +
            'and outputs the modified files in out_txt_directory'
    )
    parser_inject.add_argument('in_txt_directory',
                               help = 'The directory containing the original commu txt files')
    parser_inject.add_argument('xlsx_directory',
                               help = 'The directory containing the spreadsheets with translated data')
    parser_inject.add_argument('out_txt_directory',
                               help = 'The directory to hold the modified commu files')
    parser_inject.set_defaults(func = inject_xlsx_data)
    return parser

def generate_xlsx_files(args):
    txt_directory = args['txt_directory']
    xlsx_directory = args['xlsx_directory']
    for file_name in os.listdir(txt_directory):
        if file_name.endswith('.txt'):
            input_path = os.path.join(txt_directory, file_name)
            output_path = os.path.join(xlsx_directory, os.path.splitext(file_name)[0] + '.xlsx')

            raw_data_rows = extract_lines(input_path)
            
            # Check if there are valid lines for extraction
            if raw_data_rows:
                save_to_excel(raw_data_rows, output_path, 'Sheet1')
                print(f"Conversion completed for {file_name}")
            else:
                print(f"No valid lines found in {file_name}. Skipping...")
                
    print("Conversion to .xlsx completed successfully.")

def inject_xlsx_data(args):
    in_txt_directory = args['in_txt_directory']
    xlsx_directory = args['xlsx_directory']
    out_txt_directory = args['out_txt_directory']
    for file_name in os.listdir(in_txt_directory):
        if file_name.endswith('.txt'):
            txt_path = os.path.join(in_txt_directory, file_name)
            xlsx_path = os.path.join(xlsx_directory, os.path.splitext(file_name)[0] + '.xlsx')
            output_path = os.path.join(out_txt_directory, file_name)

            inject_translations(txt_path, xlsx_path, output_path)
            print(f"{file_name} processed")
                
    print("Translation injection completed successfully.")

def main():
    root = tk.Tk()
    root.withdraw()

    parser = create_argument_parser()
    args = parser.parse_args(sys.argv[1:])
    if 'func' in args:
        # subcommand has been selected, execute the function stored in func
        args.func(vars(args))
        return

    # otherwise use the interactive behaviour
    while True:
        try:
            option = input("GAKUEN IDOLM@STER commu text conversion tool\n1: Convert commu ADV .txt files to .xlsx files\n2: Inject commu translations from .xlsx to .txt files\n3: Exit\nChoice: ").strip()
            
            if option == '1':
                input_folder = filedialog.askdirectory(title="Select the input folder containing .txt files")
                if not input_folder:
                    raise Exception("No input folder selected.")

                output_folder = filedialog.askdirectory(title="Select the output folder for .xlsx files")
                if not output_folder:
                    raise Exception("No output folder selected.")

                generate_xlsx_files({
                    'txt_directory': input_folder,
                    'xlsx_directory': output_folder
                    })

            elif option == '2':
                input_folder = filedialog.askdirectory(title="Select the input folder containing .txt files")
                if not input_folder:
                    raise Exception("No input folder selected.")

                xlsx_folder = filedialog.askdirectory(title="Select the folder containing .xlsx files")
                if not xlsx_folder:
                    raise Exception("No .xlsx folder selected.")

                output_folder = filedialog.askdirectory(title="Select the output folder for updated .txt files")
                if not output_folder:
                    raise Exception("No output folder selected.")

                inject_xlsx_data({
                    'in_txt_directory': input_folder,
                    'xlsx_directory': xlsx_folder,
                    'out_txt_directory': output_folder
                    })

            elif option == '3':
                sys.exit(0)
            
            else:
                print("Invalid option. Please enter 1, 2, or 3.")
        
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()