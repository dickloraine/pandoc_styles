from argparse import ArgumentParser
import yaml
from .utils import file_read, file_write


class FlightScript:
    def __init__(self, func):
        setattr(self, "fligh_script", func.__get__(self))
        self.cfg, self.fmt, self.files = self.parse()

    def parse(self):
        return dict, "", []

    def fligh_script(self):
        pass

    def save_cfg(self):
        file_write("cfg.yaml", yaml.dump(self.cfg), self.cfg.get("temp-dir"))


class PreFlightScript(FlightScript):
    def parse(self):
        """Run the given script with arguments: file, cfg, fmt"""
        parser = ArgumentParser(description="Appends the string given in the metadata "
                                            "to the file")
        parser.add_argument('--cfg', nargs='?', default="",
                            help='The cfg from pandoc_styles')
        parser.add_argument('--fmt', nargs='?', default="",
                            help='The format of the file')
        args = parser.parse_args()

        cfg = yaml.load(file_read(args.cfg))
        return cfg, args.fmt, cfg["current-files"]


def run_preflight_script(func):
    script = PreFlightScript(func)
    script.fligh_script()


class PostFlightScript(FlightScript):
    def parse(self):
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

        cfg = yaml.load(file_read(args.cfg))
        return cfg, args.fmt, args.file


def run_postflight_script(func):
    script = PostFlightScript(func)
    script.fligh_script()
