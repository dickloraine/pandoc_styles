from fixtures import run_script, config_dir, copy_from_data  # pylint: disable=W0611
# pylint: disable=W0621, W0613


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
