import os
from argparse import ArgumentParser
from .constants import *  # pylint: disable=unused-wildcard-import, wildcard-import
from.make_styles_local import make_styles_local


def main():
    parser = ArgumentParser(description="Tools for pandoc styles")
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='These are the differnt tools '
                                                   'provided by this script')

    # Merge styles
    # ----------------------------------------------------------------------------------
    pmerge = subparsers.add_parser('merge', aliases=['m'],
                                   help="Merge styles")
    pmerge.add_argument('styles', nargs='*', default=[],
                        help='The styles to be merged')
    pmerge.add_argument('-f', '--style-file', default=STYLE_FILE,
                        help='Reads the styles from the given file')
    pmerge.add_argument('-n', '--style-name', default=MD_STYLE_DEF,
                        help='The name of the new style')
    pmerge.add_argument('-s', '--save-style-in-current', action='store_true',
                        help='Save the style file in the current folder')
    pmerge.set_defaults(func=make_styles_local,
                        only_merge=True,
                        metadata_file=None,
                        change_metadata_in_file=False,
                        destination=os.getcwd(),
                        save_style_in_current=False)

    # Localize styles
    # ----------------------------------------------------------------------------------
    plocal = subparsers.add_parser('localize', aliases=['l'],
                                   help="Merge styles and make them local to the current directory")
    plocal.add_argument('styles', nargs='*', default=[],
                        help='The styles to be made local')
    plocal.add_argument('-o', '--only-merge', action='store_true',
                        help='Only merge the styles, no resource files are copied')
    plocal.add_argument('-f', '--style-file', default=STYLE_FILE,
                        help='Reads the styles from the given file')
    plocal.add_argument('-m', '--metadata-file', default=None,
                        help='Reads the style names from the given file')
    plocal.add_argument('-c', '--change-metadata-in-file', action='store_true',
                        help='Change the metadata in the given file to point to the '\
                             'new style file and name')
    plocal.add_argument('-n', '--style-name', default=MD_STYLE_DEF,
                        help='The name of the new style')
    plocal.add_argument('-d', '--destination', default="assets", metavar="FOLDER",
                        help='The name of the assets folder')
    plocal.add_argument('-s', '--save-style-in-current', action='store_true',
                        help='Save the style file in the current folder')
    plocal.set_defaults(func=make_styles_local)

    # Run tool
    # ----------------------------------------------------------------------------------
    args = parser.parse_args()
    args.func(args)
