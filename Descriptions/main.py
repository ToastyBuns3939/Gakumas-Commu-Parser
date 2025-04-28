import argparse
import sys
import os

from descriptions import DescriptionStore


def create_argument_parser():
    parser = argparse.ArgumentParser(
        prog="Gakumas Card Description Parser",
        description="Gakuen Idolm@ster card description conversion tool",
    )
    subparsers = parser.add_subparsers()
    parser_shorten = subparsers.add_parser("shorten", help="Shortens json files")
    parser_shorten.add_argument("in_dir", help="The folder containing the json files")
    parser_shorten.add_argument(
        "out_dir", help="The folder to contain the output files"
    )
    parser_shorten.set_defaults(func=shorten_jsons)
    parser_lengthen = subparsers.add_parser("lengthen", help="Lengthens json files")
    parser_lengthen.add_argument(
        "in_dir", help="The folder containing the shortened json files"
    )
    parser_lengthen.add_argument(
        "out_dir", help="The folder to contain the output files"
    )
    parser_lengthen.set_defaults(func=lengthen_jsons)
    return parser

descriptions_filename = "Descriptions.json"


def shorten_jsons(args):
    in_dir = args["in_dir"]
    out_dir = args["out_dir"]
    description_store = DescriptionStore()
    basenames = [
        basename
        for basename in os.listdir(in_dir)
        if os.path.isfile(os.path.join(in_dir, basename)) and basename.endswith(".json")
    ]
    for basename in basenames:
        try:
            in_file = os.path.join(in_dir, basename)
            out_file = os.path.join(out_dir, basename)
            description_store.shorten_json(in_file, out_file)
            print(f"Shortened {basename}")
        except ValueError:
            print(f"Skipped {basename}")
    description_store.print_descriptions(os.path.join(out_dir, descriptions_filename))
    print("Written descriptions file")


def lengthen_jsons(args):
    in_dir = args["in_dir"]
    out_dir = args["out_dir"]
    description_store = DescriptionStore()
    description_store.load_descriptions(os.path.join(in_dir, descriptions_filename))
    basenames = [
        basename
        for basename in os.listdir(in_dir)
        if os.path.isfile(os.path.join(in_dir, basename))
        and basename.endswith(".json")
        and basename != descriptions_filename
    ]
    for basename in basenames:
        in_file = os.path.join(in_dir, basename)
        out_file = os.path.join(out_dir, basename)
        description_store.lengthen_json(in_file, out_file)
        print(f"Lengthened {basename}")


def main():
    parser = create_argument_parser()
    args = parser.parse_args(sys.argv[1:])
    args.func(vars(args))


if __name__ == "__main__":
    main()
