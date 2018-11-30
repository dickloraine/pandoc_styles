"""Indirectly tests update_dict too"""

from os.path import dirname, abspath, join
import pytest
import yaml
from pandoc_styles.main import PandocStyles
from pandoc_styles.utils import file_read


# pylint: disable=W0621


TEST_DIR = dirname(abspath(__file__))


@pytest.fixture
def ps():
    """Gives a PandocStyles instance"""
    return PandocStyles([join(TEST_DIR, "data", "test01.md")])


@pytest.fixture
def styles():
    return yaml.load(file_read(join(TEST_DIR, "data", "styles.yaml")))


def test_update_dict(ps, styles):
    dictionary = styles["Test_01"]["all"]
    ps.update_dict(dictionary, styles["Test_01"]["pdf"])
    assert dictionary == DICT_ALL_PDF


def test_style_to_cfg(ps, styles):
    style = styles["Test_01"]
    ps.fmt = "pdf"
    assert ps.style_to_cfg(style) == DICT_ALL_PDF
    ps.fmt = "html"
    assert ps.style_to_cfg(style) == DICT_ALL_HTML


def test_get_styles(ps, styles):
    ps.styles = styles
    ps.fmt = "pdf"
    assert ps.get_styles(styles["Test_01"]) == CFG_STYLE_01_PDF


DICT_ALL_PDF = {
    "command-line": {
        "test_01_all_cmd_01": True,
        "test_01_all_cmd_02": {
            "test_01_all_cmd_03": {
                "test_01_all_cmd_04": True,
                "test_01_all_cmd_05": [
                    "all_cmd 1",
                    "all_cmd 2"
                ],
            },
            "test_01_all_cmd_06": 3,
        },
        "test_01_all_cmd_07": "test07",
        "test_01_pdf_cmd_01": True,
        "test_01_pdf_cmd_02": {
            "test_01_pdf_cmd_03": {
                "test_01_pdf_cmd_04": True,
                "test_01_pdf_cmd_05": [
                    "pdf_cmd 1",
                    "pdf_cmd 2"
                ],
            },
            "test_01_pdf_cmd_06": 3,
        },
        "test_01_pdf_cmd_07": "test07",
    },
    "metadata": {
        "test_01_all_md_01": True,
        "test_01_all_md_02": "all_md_1",
        "test_01_all_md_03": [
            "all_md_2",
            "all_md_3"
        ],
        "test_01_pdf_md_01": True,
        "test_01_pdf_md_02": "pdf_md_1",
        "test_01_pdf_md_03": [
            "pdf_md_2",
            "pdf_md_3"
        ],
    },
}


DICT_ALL_HTML = {
    "command-line": {
        "test_01_all_cmd_01": True,
        "test_01_all_cmd_02": {
            "test_01_all_cmd_03": {
                "test_01_all_cmd_04": True,
                "test_01_all_cmd_05": [
                    "all_cmd 1",
                    "all_cmd 2",
                    "all_cmd 3",
                    "all_cmd 4"
                ],
            },
            "test_01_all_cmd_06": 3,
            "test_01_html_cmd_08": 3,
        },
        "test_01_all_cmd_07": "test07",
    },
    "metadata": {
        "test_01_all_md_01": True,
        "test_01_all_md_02": "all_md_1",
        "test_01_all_md_03": [
            "all_md_2",
            "all_md_3"
        ],
        "test_01_html_md_01": True,
        "test_01_html_md_02": "html_md_1",
        "test_01_html_md_03": [
            "html_md_2",
            "html_md_3"
        ],
    },
}

CFG_STYLE_01_PDF = {
    "command-line": {
        "test_02_all_cmd_01": True,
        "test_02_all_cmd_02": {
            "test_02_all_cmd_03": {
                "test_02_all_cmd_04": True,
                "test_02_all_cmd_05": [
                    "all_cmd 3",
                    "all_cmd 4"
                ]
            },
            "test_02_all_cmd_06": 3,
        },
        "test_02_all_cmd_07": "test07",
        "test_02_pdf_cmd_01": True,
        "test_02_pdf_cmd_02": {
            "test_02_pdf_cmd_03": {
                "test_02_pdf_cmd_04": True,
                "test_02_pdf_cmd_05": [
                    "pdf_cmd 3",
                    "pdf_cmd 4"
                ],
            },
            "test_02_pdf_cmd_06": 3,
        },
        "test_02_pdf_cmd_07": "test07",
        "test_01_all_cmd_01": True,
        "test_01_all_cmd_02": {
            "test_01_all_cmd_03": {
                "test_01_all_cmd_04": True,
                "test_01_all_cmd_05": [
                    "all_cmd 1",
                    "all_cmd 2"
                ],
            },
            "test_01_all_cmd_06": 3,
        },
        "test_01_all_cmd_07": "test07",
        "test_01_pdf_cmd_01": True,
        "test_01_pdf_cmd_02": {
            "test_01_pdf_cmd_03": {
                "test_01_pdf_cmd_04": True,
                "test_01_pdf_cmd_05": [
                    "pdf_cmd 1",
                    "pdf_cmd 2"
                ],
            },
            "test_01_pdf_cmd_06": 3,
        },
        "test_01_pdf_cmd_07": "test07",
    },
    "metadata": {
        "test_02_all_md_01": True,
        "test_02_all_md_02": "all_md_1",
        "test_02_all_md_03": [
            "all_md_4",
            "all_md_5"
        ],
        "test_02_pdf_md_01": True,
        "test_02_pdf_md_02": "pdf_md_1",
        "test_02_pdf_md_03": [
            "pdf_md_4",
            "pdf_md_5"
        ],
        "test_01_all_md_01": True,
        "test_01_all_md_02": "all_md_1",
        "test_01_all_md_03": [
            "all_md_2",
            "all_md_3"
        ],
        "test_01_pdf_md_01": True,
        "test_01_pdf_md_02": "pdf_md_1",
        "test_01_pdf_md_03": [
            "pdf_md_2",
            "pdf_md_3"
        ],
    },
}
