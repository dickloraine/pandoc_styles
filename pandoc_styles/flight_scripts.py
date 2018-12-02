from argparse import ArgumentParser
import yaml
from .constants import CFG_TEMP_FILE, MD_TEMP_DIR, MD_CURRENT_FILES, FMT, OUTPUT_FILE
from .utils import file_read, file_write


class FlightScript:
    def __init__(self, func, flight_type):
        setattr(self, "fligh_script", func.__get__(self))

        parser = ArgumentParser(description="")
        parser.add_argument('--cfg', nargs='?', default="",
                            help='The cfg from pandoc_styles')
        args = parser.parse_args()

        self.cfg = yaml.load(file_read(args.cfg))
        self.fmt = self.cfg[FMT]
        if flight_type == "preflight":
            self.files = self.cfg[MD_CURRENT_FILES]
        else:
            self.file = self.cfg[OUTPUT_FILE]

    def fligh_script(self):
        pass

    def save_cfg(self):
        file_write(CFG_TEMP_FILE, yaml.dump(self.cfg), self.cfg.get(MD_TEMP_DIR))


def run_preflight_script(func):
    script = FlightScript(func, "preflight")
    script.fligh_script()


def run_postflight_script(func):
    script = FlightScript(func, "postflight")
    script.fligh_script()
