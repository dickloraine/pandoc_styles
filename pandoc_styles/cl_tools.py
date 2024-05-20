from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from .cl_stylepacks import import_style_pack, remove_style_pack
from .constants import *  # noqa F403


def main():
    parser = ArgumentParser(
        description="Tools for pandoc styles",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        title="Tools",
        description="""Additional help is available if these are used with the help
                    option.""",
    )

    # Import style-pack
    # ----------------------------------------------------------------------------------
    pimport = subparsers.add_parser(
        "import",
        aliases=["i"],
        formatter_class=ArgumentDefaultsHelpFormatter,
        help="Import the given stylepack",
    )
    pimport.add_argument("stylepack", help="The stylepack to import")
    pimport.add_argument(
        "--url", "-u", default=None, help="Download the stylepack from the given url."
    )
    pimport.add_argument(
        "--global",
        "-g",
        action="store_true",
        dest="is_global",
        help="Add the style pack content to the user folders and "
        "integrate the style into the global styles.yaml",
    )
    pimport.set_defaults(func=import_style_pack)

    # Remove style-pack
    # ----------------------------------------------------------------------------------
    premove = subparsers.add_parser(
        "remove",
        aliases=["r"],
        formatter_class=ArgumentDefaultsHelpFormatter,
        help="Remove the given stylepack. Does not work "
        "for globaly installed packs.",
    )
    premove.add_argument("packname", help="The stylepack to remove")
    premove.set_defaults(func=remove_style_pack)

    # Run tool
    # ----------------------------------------------------------------------------------
    args = parser.parse_args()
    if "func" not in args:
        parser.print_help()
        return
    args.func(args)
