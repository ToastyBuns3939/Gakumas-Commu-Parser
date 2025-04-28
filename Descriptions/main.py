import argparse
import sys
import os

from descriptions import DescriptionStore, shorten_json


def create_argument_parser():
    parser = argparse.ArgumentParser(
        prog="Gakumas Card Description Parser",
        description="Gakuen Idolm@ster card description conversion tool",
    )
    subparsers = parser.add_subparsers()
    parser_extract = subparsers.add_parser("shorten", help="Shortens json files")
    parser_extract.add_argument("json_dir", help="The folder containing the json files")
    parser_extract.add_argument(
        "out_dir", help="The folder to contain the output files"
    )
    return parser


def shorten_jsons(json_dir: str, out_dir: str):
    description_store = DescriptionStore()
    basenames = [
        file
        for file in os.listdir(json_dir)
        if os.path.isfile(os.path.join(json_dir, file)) and file.endswith(".json")
    ]
    for basename in basenames:
        try:
            json_file = os.path.join(json_dir, basename)
            out_file = os.path.join(out_dir, basename)
            shorten_json(description_store, json_file, out_file)
            print(f"Shortened {basename}")
        except ValueError:
            print(f"Skipped {basename}")
    description_store.print_descriptions(os.path.join(out_dir, "Descriptions.json"))
    print("Written descriptions file")


def main():
    parser = create_argument_parser()
    args = parser.parse_args(sys.argv[1:])
    shorten_jsons(vars(args)["json_dir"], vars(args)["out_dir"])


if __name__ == "__main__":
    main()
