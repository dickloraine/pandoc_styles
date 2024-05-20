from argparse import ArgumentParser
from os.path import join

from .constants import (
    CFG_TEMP_FILE,
    EPUB,
    FMT,
    HTML,
    LATEX,
    LATEX_FORMATS,
    MD_CURRENT_FILES,
    MD_TEMP_DIR,
    OUTPUT_FILE,
)
from .utils import yaml_dump, yaml_load


class FlightScript:
    def __init__(self, func, flight_type):
        setattr(self, "fligh_script", func.__get__(self))

        parser = ArgumentParser(description="")
        parser.add_argument(
            "--cfg", nargs="?", default="", help="The cfg from pandoc_styles"
        )
        args = parser.parse_args()

        self.cfg = yaml_load(args.cfg)
        self.fmt = self.cfg[FMT]
        self.real_fmt = self.fmt
        if self.fmt in LATEX_FORMATS:
            self.fmt = LATEX
        elif self.fmt == EPUB:
            self.fmt = HTML

        if flight_type == "preflight":
            self.files = self.cfg[MD_CURRENT_FILES]
        else:
            self.file = self.cfg[OUTPUT_FILE]

    def fligh_script(self):
        pass

    def save_cfg(self):
        yaml_dump(self.cfg, join(self.cfg.get(MD_TEMP_DIR), CFG_TEMP_FILE))


def run_preflight_script(func):
    script = FlightScript(func, "preflight")
    script.fligh_script()


def run_postflight_script(func):
    script = FlightScript(func, "postflight")
    script.fligh_script()
