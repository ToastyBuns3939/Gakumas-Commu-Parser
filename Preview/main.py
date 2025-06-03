import argparse
import json
import sys
import openpyxl
from openpyxl.worksheet.formula import ArrayFormula
from pathlib import Path


def create_argument_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser_preview = subparsers.add_parser("preview", help="Create xlsx preview")
    parser_preview.add_argument("in_file", help="Input json file")
    parser_preview.add_argument("out_file", help="Output xlsx file")
    parser_preview.set_defaults(func=create_preview_xlsx)
    return parser


def get_original_formula(row_index):
    desc_cells = f"OFFSET($F{row_index}, 0, 0, 1, $E{row_index})"
    return ArrayFormula(f"C{row_index}", f'=TEXTJOIN("", FALSE, {desc_cells})')


def get_translation_formula(ref_sheet_name, row_index):
    desc_cells = f"OFFSET($F{row_index}, 0, 0, 1, $E{row_index})"
    search_range = f"{ref_sheet_name}!$A:$B"
    search = f"VLOOKUP({desc_cells}, {search_range}, 2, false)"
    return ArrayFormula(
        f"D{row_index}",
        f'=TEXTJOIN("", FALSE, IFERROR({search}, {desc_cells}))',
    )


def create_preview_xlsx(args):
    in_filename = args["in_file"]
    out_filename = args["out_file"]
    file_stem = Path(in_filename).stem

    in_file = open(in_filename, encoding="utf8")
    json_object = json.load(in_file)
    in_file.close()
    data = json_object["data"]
    rows = [
        [
            "Id",
            "Name",
            "Original",
            "Translation",
            "Number of description parts",
            "Description parts",
        ],
    ] + [
        [
            item["id"],
            item.get("name", ""),
            get_original_formula(index + 2),
            get_translation_formula(file_stem, index + 2),
            len(item["produceDescriptions"]),
        ]
        + [desc["text"] for desc in item["produceDescriptions"]]
        for index, item in enumerate(data)
    ]

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = file_stem + "-preview"
    for row in rows:
        worksheet.append(row)
    workbook.save(out_filename)


def main():
    parser = create_argument_parser()
    args = parser.parse_args(sys.argv[1:])
    args.func(vars(args))


if __name__ == "__main__":
    main()
