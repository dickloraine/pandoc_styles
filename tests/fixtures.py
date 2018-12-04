from shutil import copy, copytree
from os.path import dirname, abspath, join, expanduser, pardir
import subprocess
import pytest


TEST_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(TEST_DIR, "data")
TEST_CONFIG_DIR = abspath(join(TEST_DIR, pardir, "pandoc_styles", "config_dir"))
POETRY = f'python {join(expanduser("~"), ".poetry/bin/poetry")}'
# pylint: disable=W0621, W0613, W1401


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
    copytree(TEST_CONFIG_DIR, config_dir)
    return config_dir


@pytest.fixture
def copy_from_data(tmpdir):
    def _copy_from_data(*files):
        for f in files:
            copy(join(TEST_DATA_DIR, f), tmpdir)
    return _copy_from_data

@pytest.fixture
def copy_from_config(tmpdir):
    def _copy_from_config(*files):
        for f in files:
            copy(join(TEST_CONFIG_DIR, f), tmpdir)
    return _copy_from_config
