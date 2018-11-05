"""
Call an external script to run over the output-file. Use <file> in the command-line
options for the path to the file.
"""
from pandoc_styles import run_postflight_script, run_process


def postflight(self):
    for command in self.cfg.get("postflight-apps", []):
        command = command.replace("<file>", "{}")
        run_process(command.format(self.files))


if __name__ == '__main__':
    run_postflight_script(postflight)
