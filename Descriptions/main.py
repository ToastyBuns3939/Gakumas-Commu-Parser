import argparse
import sys

from descriptions import shorten_json


def create_argument_parser():
    parser = argparse.ArgumentParser(
        prog="Gakumas Card Description Parser",
        description="Gakuen Idolm@ster card description conversion tool",
    )
    subparsers = parser.add_subparsers()
    parser_extract = subparsers.add_parser("extract", help="Extracts data")
    parser_extract.add_argument("json_file", help="The json file")
    parser_extract.add_argument("output_file", help="The output file")
    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args(sys.argv[1:])
    shorten_json(vars(args)["json_file"], vars(args)["output_file"])


if __name__ == "__main__":
    main()
