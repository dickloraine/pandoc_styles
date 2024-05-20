"""
stylepack files have a naming convention:
stylepackname.zip or
stylepackname_v1.1.zip
"""

import re
import shutil
import zipfile as zf
from distutils.dir_util import copy_tree
from os import path
from tempfile import TemporaryDirectory
from urllib.request import urlcleanup, urlretrieve

from .constants import CONFIG_DIR, DEFAULT_STYLE, PATH_STYLE, STYLE_FILE
from .utils import get_file_name, yaml_dump, yaml_load


def import_style_pack(args):
    if args.url:
        stylepack_name = args.stylepack
        try:
            stylepack_file, _ = urlretrieve(args.url)
        except:
            urlcleanup()
            raise
    elif path.isfile(args.stylepack):
        stylepack_file = args.stylepack
        stylepack_name = get_file_name(args.stylepack)
    else:
        stylepack_name = args.stylepack
        stylepack_file = f"{stylepack_name}.zip"

    stylepack_name_ = re.match(r"(.*?)_v\d", stylepack_name)
    stylepack_name = stylepack_name.group(1) if stylepack_name_ else stylepack_name

    if not args.is_global:
        args.packname = stylepack_name
        remove_style_pack(args)
        with zf.ZipFile(stylepack_file) as f:
            f.extractall(path.join(CONFIG_DIR, PATH_STYLE))
    else:
        with TemporaryDirectory() as tmpdir:
            with zf.ZipFile(stylepack_file) as f:
                f.extractall(tmpdir)
            copy_tree(path.join(tmpdir, stylepack_name), CONFIG_DIR)

            styles = yaml_load(
                path.join(tmpdir, stylepack_name, f"{stylepack_name}.yaml")
            )
            del styles[DEFAULT_STYLE]
            global_styles = yaml_load(STYLE_FILE)
            for k, v in styles.items():
                global_styles[k] = v
            yaml_dump(global_styles, STYLE_FILE)

    if args.url:
        urlcleanup()


def remove_style_pack(args):
    style_folder = path.join(CONFIG_DIR, PATH_STYLE, args.packname)
    if path.isdir(style_folder):
        shutil.rmtree(style_folder)
