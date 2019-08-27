from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from .constants import *  # pylint: disable=unused-wildcard-import, wildcard-import
from .cl_make_styles_local import make_styles_local
from .cl_stylepacks import import_style_pack, remove_style_pack


def main():
    parser = ArgumentParser(description="Tools for pandoc styles",
                            formatter_class=ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(
        title='Tools',
        description='''Additional help is available if these are used with the help
                    option.''')

    # Import style-pack
    # ----------------------------------------------------------------------------------
    pimport = subparsers.add_parser('import', aliases=['i'],
                                    formatter_class=ArgumentDefaultsHelpFormatter,
                                    help='Import the given style-pack')
    pimport.add_argument('stylepack',
                         help='The style-pack to import')
    pimport.set_defaults(func=import_style_pack)

    # Remove style-pack
    # ----------------------------------------------------------------------------------
    premove = subparsers.add_parser('remove', aliases=['r'],
                                    formatter_class=ArgumentDefaultsHelpFormatter,
                                    help='Remove the given style-pack')
    premove.add_argument('packname',
                         help='The style-pack to remove')
    premove.set_defaults(func=remove_style_pack)

    # Merge styles
    # ----------------------------------------------------------------------------------
    pmerge = subparsers.add_parser('merge', aliases=['m'],
                                   formatter_class=ArgumentDefaultsHelpFormatter,
                                   help='Merge styles')
    pmerge.add_argument('styles', nargs='*', default=[],
                        help='The styles to merge')
    pmerge.add_argument('--style-file', '-f', default=STYLE_FILE,
                        help='Read the styles from the given file')
    pmerge.add_argument('--style-name', '-n', default=DEFAULT_STYLE,
                        help='The name of the new style')
    pmerge.add_argument('--output-file', '-t', default="style.yaml",
                        help='The name of the generated style file')
    pmerge.set_defaults(func=make_styles_local,
                        only_merge=True,
                        metadata_file=None,
                        change_metadata_in_file=False,
                        destination="",
                        save_style_in_current=True)

    # Localize styles
    # ----------------------------------------------------------------------------------
    plocal = subparsers.add_parser('localize', aliases=['l'],
                                   formatter_class=ArgumentDefaultsHelpFormatter,
                                   help='''Merge styles and make them local to the
                                        current directory''')
    plocal.add_argument('styles', nargs='*', default=[],
                        help='The styles to make local')
    plocal.add_argument('--only-merge', '-o', action='store_true',
                        help='Only merge the styles, no resource files are copied')
    plocal.add_argument('--style-file', '-f', default=STYLE_FILE,
                        help='Read the styles from the given file')
    plocal.add_argument('--metadata-file', '-m', default=None,
                        help='Reads the style names from the given file')
    plocal.add_argument('--change-metadata-in-file', '-c', action='store_true',
                        help='Change the metadata in the given file to point to the '
                             'new style file and name')
    plocal.add_argument('--style-name', '-n', default=DEFAULT_STYLE,
                        help='The name of the new style')
    plocal.add_argument('--output-file', '-t', default="style.yaml",
                        help='The name of the generated style file')
    plocal.add_argument('--destination', '-d', default="assets", metavar="FOLDER",
                        help='The name of the assets folder')
    plocal.add_argument('--save-style-in-current', '-s', action='store_true',
                        help='Save the style file in the current folder')
    plocal.set_defaults(func=make_styles_local)

    # Run tool
    # ----------------------------------------------------------------------------------
    args = parser.parse_args()
    args.func(args)
