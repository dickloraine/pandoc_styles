import pytest
from fixtures import run_script, config_dir, copy_from_data  # pylint: disable=W0611
# pylint: disable=W0621, W0613


@pytest.fixture
def run_app(run_script, copy_from_data):
    def _run_app(files, data_files=None, extra_args="", formats=None, output=""):
        copy_from_data(*files)
        if data_files:
            copy_from_data(*data_files)
        formats = formats or ["html", "epub", "pdf"]
        cmd = f"{' '.join(files)} {extra_args} -t {' '.join(formats)}"
        output = output or "".join(f"INFO: Build {fmt}\n" for fmt in formats)
        ps = run_script(cmd)
        assert ps
        assert ps.stdout == output
    return _run_app


def test_app_without_user_dir(run_app):
    run_app(["test01.md"], ["cover.jpg"])


def test_app(config_dir, run_app):
    run_app(["test02.md"], ["cover.jpg"])
