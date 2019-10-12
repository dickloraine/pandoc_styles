from os.path import join
from copy import deepcopy
import pytest
from pandoc_styles.main import PandocStyles
from pandoc_styles.constants import *  # pylint: disable=W0401, W0614
from pandoc_styles.utils import yaml_load
from fixtures import TEST_DATA_DIR
# pylint: disable=W0621, protected-access


@pytest.fixture
def test_file():
    return join(TEST_DATA_DIR, "test01.md")


@pytest.fixture
def styles():
    return yaml_load(join(TEST_DATA_DIR, "styles.yaml"))


@pytest.fixture
def ps(test_file):
    """Gives a PandocStyles instance"""
    return PandocStyles([test_file], style_file=join(TEST_DATA_DIR, "styles.yaml"))


def test_update_dict(ps, styles):
    dictionary = deepcopy(styles["Test_01"]["all"])
    ps.update_dict(dictionary, styles["Test_01"]["pdf"])
    assert dictionary == DICT_ALL_PDF
    dictionary = deepcopy(styles["Test_01"]["all"])
    ps.update_dict(dictionary, styles["Test_01"]["html"])
    assert dictionary == DICT_ALL_HTML


def test_style_to_cfg(ps, styles):
    style = styles["Test_01"]
    assert ps.style_to_cfg(style, "pdf") == DICT_ALL_PDF
    assert ps.style_to_cfg(style, "html") == DICT_ALL_HTML


def test_get_pandoc_metadata(ps, test_file):
    test_against = yaml_load(join(TEST_DATA_DIR, "test01_only_yaml.yaml"))
    metadata_file = None
    assert ps.get_pandoc_metadata(metadata_file or test_file) == test_against
    metadata_file = join(TEST_DATA_DIR, "test01_only_yaml.yaml")
    assert ps.get_pandoc_metadata(metadata_file or None) == test_against
    test_file = join(TEST_DATA_DIR, "no_metadata.md")
    assert ps.get_pandoc_metadata(test_file) == {}


def test_get_cfg(test_file):
    ps = PandocStyles([test_file], style_file=join(TEST_DATA_DIR, "styles.yaml"),
                      use_styles=["Test_01"])
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
        MD_TEMPLATE_VARIABLES: {},
        MD_STYLE_PACKS: [],
        MD_CURRENT_FILES: [test_file],
        OUTPUT_FILE: "test01.pdf",
        FMT: "pdf",
        TO_FMT: LATEX,
        MD_TEMP_DIR: temp_dir,
        MD_CFG_DIR: CONFIG_DIR,
    })
    assert ps._get_cfg("pdf") == test_against


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
    "style": "Func_test"
}
