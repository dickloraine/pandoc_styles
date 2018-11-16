"""Indirectly tests update_dict too"""

from os.path import dirname, abspath
import yaml
from pandoc_styles.main import PandocStyles
from pandoc_styles.utils import file_read, change_dir


def test_style_to_cfg():
    test_dir = dirname(abspath(__file__))
    with change_dir(test_dir):
        ps = PandocStyles(["./data/test01.md"], None, "", None, "", "", "",
                          "./data/styles.yaml")
        style = yaml.load(file_read("./data/styles.yaml"))
        style = style["Test_01"]
        ps.fmt = "pdf"
        assert ps.style_to_cfg(style) == {
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

        ps.fmt = "html"
        assert ps.style_to_cfg(style) == {
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
