import os
import sys
import tkinter as tk
from tkinter import filedialog
from extract_lines import extract_lines
from save_to_excel import save_to_excel
from inject_translations import inject_translations

def main():
    root = tk.Tk()
    root.withdraw()

    while True:
        try:
            option = input("GAKUEN IDOLM@STER commu text conversion tool\n1: Convert .txt files to .xlsx files\n2: Inject translations from .xlsx to .txt files\n3: Exit\nChoice: ").strip()
            
            if option == '1':
                input_folder = filedialog.askdirectory(title="Select the input folder containing .txt files")
                if not input_folder:
                    raise Exception("No input folder selected.")

                output_folder = filedialog.askdirectory(title="Select the output folder for .xlsx files")
                if not output_folder:
                    raise Exception("No output folder selected.")

                for file_name in os.listdir(input_folder):
                    if file_name.endswith('.txt'):
                        input_path = os.path.join(input_folder, file_name)
                        output_path = os.path.join(output_folder, os.path.splitext(file_name)[0] + '.xlsx')

                        names, texts, types, _, _, _ = extract_lines(input_path)
                        
                        # Check if there are valid lines for extraction
                        if names:
                            save_to_excel(names, texts, types, output_path, 'Sheet1')
                            print(f"Conversion completed for {file_name}")
                        else:
                            print(f"No valid lines found in {file_name}. Skipping...")
                
                print("Conversion to .xlsx completed successfully.")

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

                for file_name in os.listdir(input_folder):
                    if file_name.endswith('.txt'):
                        txt_path = os.path.join(input_folder, file_name)
                        xlsx_path = os.path.join(xlsx_folder, os.path.splitext(file_name)[0] + '.xlsx')
                        output_path = os.path.join(output_folder, file_name)

                        inject_translations(txt_path, xlsx_path, output_path)
                        print(f"{file_name} processed")
                
                print("Translation injection completed successfully.")

            elif option == '3':
                sys.exit(0)
            
            else:
                print("Invalid option. Please enter 1, 2, or 3.")
        
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()