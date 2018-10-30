from argparse import ArgumentParser
import yaml
from .utils import file_read


def run_preflight_script(func):
    """Run the given script with arguments: file, cfg, fmt"""
    parser = ArgumentParser(description="Appends the string given in the metadata "
                                        "to the file")
    parser.add_argument('files', nargs='*', default=[],
                        help='The source file to be converted')
    parser.add_argument('--cfg', nargs='?', default="",
                        help='The cfg from pandoc_styles')
    parser.add_argument('--fmt', nargs='?', default="",
                        help='The format of the file')
    args = parser.parse_args()

    if args.cfg:
        args.cfg = yaml.load(file_read(args.cfg))
    func(args.files, args.cfg, args.fmt)



def run_postflight_script(func):
    """Run the given script with arguments: file, cfg, fmt"""
    parser = ArgumentParser(description="Appends the string given in the metadata "
                                        "to the file")
    parser.add_argument('file', nargs='?', default=None,
                        help='The source file to be converted')
    parser.add_argument('--cfg', nargs='?', default="",
                        help='The cfg from pandoc_styles')
    parser.add_argument('--fmt', nargs='?', default="",
                        help='The format of the file')
    args = parser.parse_args()

    if args.cfg:
        args.cfg = yaml.load(file_read(args.cfg))
    func(args.file, args.cfg, args.fmt)
