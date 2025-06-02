import argparse
import json
import sys
import openpyxl


def create_argument_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser_preview = subparsers.add_parser("preview", help="Create xlsx preview")
    parser_preview.add_argument("in_file", help="Input json file")
    parser_preview.add_argument("out_file", help="Output xlsx file")
    parser_preview.set_defaults(func=create_preview_xlsx)
    return parser


def create_preview_xlsx(args):
    in_filename = args["in_file"]
    out_filename = args["out_file"]

    in_file = open(in_filename, encoding="utf8")
    json_object = json.load(in_file)
    in_file.close()
    data = json_object["data"]
    rows = [
        [item["id"], item["upgradeCount"], len(item["produceDescriptions"]), ""]
        + [desc["text"] for desc in item["produceDescriptions"]]
        for item in data
    ]

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "ProduceCard-preview"
    for row in rows:
        worksheet.append(row)
    workbook.save(out_filename)


def main():
    parser = create_argument_parser()
    args = parser.parse_args(sys.argv[1:])
    args.func(vars(args))


if __name__ == "__main__":
    main()
