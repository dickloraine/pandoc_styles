from shutil import copy, copytree
from os.path import dirname, abspath, join, expanduser
import subprocess
import pytest
# pylint: disable=W0621, W0613


TEST_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(TEST_DIR, "data")
POETRY = f'python {join(expanduser("~"), ".poetry/bin/poetry")}'


@pytest.fixture
def run_script(tmpdir):
    copy(join(TEST_DATA_DIR, "styles.yaml"), tmpdir)
    def _run_script(args):
        return subprocess.run(f'{POETRY} run pandoc_styles --style-file=styles.yaml '
                              f'-w "{tmpdir}" {args}', stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, shell=True)
    return _run_script


@pytest.fixture
def config_dir(tmpdir):
    config_dir = join(tmpdir, "config_dir")
    copytree("./pandoc_styles/config_dir", config_dir)
    return config_dir


@pytest.fixture
def copy_from_data(tmpdir):
    def _copy_from_data(*files):
        for f in files:
            copy(join(TEST_DATA_DIR, f), tmpdir)
    return _copy_from_data


def test_app(run_script, copy_from_data):
    copy_from_data("test01.md", "cover.jpg")
    ps = run_script("test01.md -t html epub pdf")
    assert ps.returncode == 0
    assert ps.stdout == "INFO: Build html\nINFO: Build epub\nINFO: Build pdf\n"


def test_app2(config_dir, run_script, copy_from_data):
    copy_from_data("test02.md")
    ps = run_script("test02.md -t html pdf")
    assert ps.returncode == 0
    assert ps.stdout == "INFO: Build html\nINFO: Build pdf\n"
