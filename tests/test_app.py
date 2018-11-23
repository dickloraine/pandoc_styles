from shutil import copy
from os.path import dirname, abspath, join, expanduser
import subprocess
from pandoc_styles.utils import change_dir


def poetry_cmd():
    return f'python {join(expanduser("~"), ".poetry/bin/poetry")}'

def test_app(tmpdir):
    test_dir = dirname(abspath(__file__))
    with change_dir(test_dir):
        copy("./data/test01.md", tmpdir)
        copy("./data/cover.jpg", tmpdir)
        copy("./data/styles.yaml", tmpdir)

    ps = subprocess.run(f'{poetry_cmd()} run pandoc_styles test01.md -t html epub pdf '\
                        f'--style-file=styles.yaml -w {tmpdir}',
                        stdout=subprocess.PIPE, text=True)
    assert ps.returncode == 0
    assert ps.stdout == "INFO: Build html\nINFO: Build epub\nINFO: Build pdf\n"
