from os.path import dirname, abspath, join
from copy import deepcopy
import pytest
import yaml
from pandoc_styles.main import PandocStyles
from pandoc_styles.constants import *  # pylint: disable=W0401, W0614
from pandoc_styles.utils import file_read


# pylint: disable=W0621


TEST_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(TEST_DIR, "data")


@pytest.fixture
def test_file():
    """Gives a PandocStyles instance"""
    return join(TEST_DATA_DIR, "test01.md")


@pytest.fixture
def styles():
    return yaml.safe_load(file_read(join(TEST_DATA_DIR, "styles.yaml")))


@pytest.fixture
def ps(test_file):
    """Gives a PandocStyles instance"""
    return PandocStyles([test_file])


def test_update_dict(ps, styles):
    dictionary = styles["Test_01"]["all"]
    ps.update_dict(dictionary, styles["Test_01"]["pdf"])
    assert dictionary == DICT_ALL_PDF


def test_style_to_cfg(ps, styles):
    style = styles["Test_01"]
    assert ps.style_to_cfg(style, "pdf") == DICT_ALL_PDF
    assert ps.style_to_cfg(style, "html") == DICT_ALL_HTML


def test_get_styles(ps, styles):
    ps.styles = styles
    assert ps.get_styles(styles["Test_01"], "pdf") == CFG_STYLE_01_PDF


def test_get_pandoc_metadata(ps, test_file):
    ps.metadata = test_file
    assert ps.get_pandoc_metadata() == yaml.safe_load(file_read("test01_only_yaml.yaml",
                                                                TEST_DATA_DIR))


def test_get_cfg(ps, styles, test_file):
    ps.styles = styles
    ps.use_styles = ["Test_01"]
    temp_dir = ps.temp_dir
    test_against = deepcopy(CFG_STYLE_01_PDF)
    test_against.update({
        "title": "Test",
        "author": "Test Author",
        "language": "en-US",
        "description": "This is the description of the novel.\n",
        "dedication": "_for Elise_",
        "copyrights": "test copyrights  \nin more than  \none line\n",
        "cover-image": "./cover.jpg",
        "formats": ["pdf", "html"],
        "style": "Func_test",
        MD_CURRENT_FILES: [test_file],
        OUTPUT_FILE: join(TEST_DIR, "data", "test01.pdf"),
        FMT: "pdf",
        TO_FMT: LATEX,
        MD_TEMP_DIR: temp_dir,
        MD_CFG_DIR: CONFIG_DIR,
    })
    assert ps.get_cfg("pdf") == test_against


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
