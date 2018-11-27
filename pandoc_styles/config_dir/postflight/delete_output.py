"""
Delete the output file. Usefull, if you need the converted file only as an intermediate.
"""
from os import remove
from pandoc_styles import run_postflight_script


def postflight(self):
    remove(self.files)


if __name__ == '__main__':
    run_postflight_script(postflight)
