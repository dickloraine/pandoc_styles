import re
from os import makedirs
from os.path import join, isfile
from shutil import copy, SameFileError
from functools import partial

from .main import PandocStyles
from .constants import *  # pylint: disable=unused-wildcard-import, wildcard-import
from .utils import (make_list, file_read, file_write, has_extension, yaml_load,
                    yaml_dump, yaml_dump_pandoc_md, expand_directories, get_file_name)


def make_styles_local(args):
    styles = args.styles
    metadata = PandocStyles.get_pandoc_metadata(args.metadata_file)
    styles_from_file, style_definition, style_file = get_styles(metadata, args.style_file)
    style_pack = None if get_file_name(style_file) == "styles" \
                 else get_file_name(style_file)
    if style_pack and not styles_from_file:
        styles_from_file = [DEFAULT_STYLE]
    styles.extend(styles_from_file)
    if not styles:
        print("No styles found!")
        return

    style = merge_styles(styles, style_file)
    if style_definition:
        PandocStyles.update_dict(style, style_definition)
    if not args.only_merge:
        copy_files(style, args.destination, style_pack)
    output_file = args.output_file if args.save_style_in_current \
                  else join(args.destination, args.output_file)
    yaml_dump({args.style_name: style}, output_file)
    if args.change_metadata_in_file and args.metadata_file:
        change_metadata(args.metadata_file, metadata, args.style_name, output_file)


def get_styles(md, style_file):
    if not md:
        return [], None, style_file
    styles = make_list(md.get(MD_STYLE, []))
    style_definition = md.get(MD_STYLE_DEF)
    style_file = expand_directories(md.get(MD_STYLE_FILE, style_file))
    return styles, style_definition, style_file


def merge_styles(styles, style_file):
    """Merge multiple styles into one."""
    source_styles = yaml_load(style_file)
    new_style = source_styles.get(ALL_STYLE, {})
    new_style[MD_INHERITS] = list(styles)
    new_style = _get_styles(new_style, source_styles)
    del new_style[MD_INHERITS]
    new_style = dict(sorted(new_style.items()))
    return new_style


def _get_styles(style, source_styles):
    """
    Gets the data for all inherited styles
    """
    if not style.get(MD_INHERITS):
        return style
    cfg = dict()
    for extra_style in make_list(style[MD_INHERITS]):
        extra_style = _get_styles(source_styles[extra_style], source_styles)
        PandocStyles.update_dict(cfg, extra_style)
    PandocStyles.update_dict(cfg, style)
    return cfg


def copy_files(style, destination, style_pack):
    copy_in_group = partial(_copy_files_in_group, destination, style_pack)
    for group in style.values():
        copy_in_group(group, MD_CMD_LINE, "filter")
        copy_in_group(group, MD_PREFLIGHT)
        copy_in_group(group, MD_POSTFLIGHT)
        copy_in_group(group, MD_SASS, "files", PATH_SASS)
        copy_in_group(group, MD_CMD_LINE, "template")


def _copy_files_in_group(destination, style_pack, group, section, field=None, key=None):
    if field is None:
        old = group.get(section)
        key = key or section
    else:
        old = group.get(section, {}).get(field)
        key = key or field
    if not old:
        return

    if isinstance(old, list):
        new = []
        for f in old:
            new.append(_copy_expanded_file(f, key, destination, style_pack))
    else:
        new = _copy_expanded_file(old, key, destination, style_pack)

    if old != new:
        if field is None:
            group[section] = new
        else:
            group[section][field] = new


def _copy_expanded_file(f, key, destination, style_pack):
    path = expand_directories(f, key, style_pack)
    if isfile(path):
        new_path = f"./{destination}/{key}/"
        makedirs(new_path, exist_ok=True)
        try:
            path = copy(path, new_path)
        except SameFileError:
            pass
    return path


def change_metadata(md_file, md, style_name, output_file):
    if style_name != DEFAULT_STYLE:
        md[MD_STYLE] = style_name
    elif md.get(MD_STYLE):
        del md[MD_STYLE]
    md[MD_STYLE_FILE] = "./" + output_file.replace("\\", "/")
    del md[MD_STYLE_DEF]

    if has_extension(md_file, ["yaml", "yml"]):
        yaml_dump(md, md_file)

    repl = yaml_dump_pandoc_md(md)
    text = file_read(md_file)
    old_text = text
    text = re.sub(r'.?-{3}(.*?)(\n\.{3}\n|\n-{3}\n)', repl, text, 1, re.DOTALL)
    if text != old_text:
        file_write(md_file, text)
