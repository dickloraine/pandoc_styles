import os
from os import path
import shutil
from zipfile import ZipFile
from .constants import CONFIG_DIR, PATH_STYLE


def import_style_pack(args):
    with ZipFile(args.stylepack) as zf:
        zf.extractall(CONFIG_DIR)


def remove_style_pack(args):
    style_file = path.join(CONFIG_DIR, f"{args.packname}.yaml")
    if path.isfile(style_file):
        os.remove(style_file)

    style_folder = path.join(CONFIG_DIR, PATH_STYLE, args.packname)
    if path.isdir(style_folder):
        shutil.rmtree(style_folder)
