"""
Call an external script to run over all files. Use <file> in the command-line options
for the path to the current file.
"""
from pandoc_styles import run_preflight_script, run_process


def preflight(files, cfg, fmt):
    for command in cfg.get("preflight-apps", []):
        command = command.replace("<file>", "{}")
        for ffile in files:
            run_process(command.format(ffile))


if __name__ == '__main__':
    run_preflight_script(preflight)
