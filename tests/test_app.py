from shutil import copy
from os.path import dirname, abspath
import subprocess
from pandoc_styles.utils import change_dir


def test_app(tmpdir):
    test_dir = dirname(abspath(__file__))
    with change_dir(test_dir):
        copy("./data/test01.md", tmpdir)
        copy("./data/cover.jpg", tmpdir)
        copy("./data/styles.yaml", tmpdir)
    with change_dir(tmpdir):
        ps = subprocess.run('pandoc_styles test01.md -t html epub pdf',
                            capture_output=True, text=True)
        assert ps.returncode == 0
        assert ps.stderr == "INFO: Build html\nINFO: Build epub\nINFO: Build pdf\n"
