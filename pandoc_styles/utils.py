"""Some utility functions"""

import logging
import shlex
import subprocess
from contextlib import contextmanager
from os import chdir, getcwd
from os.path import isdir, isfile, join, normpath, split, splitext

from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

from .constants import CONFIG_DIR, PATH_MISC, PATH_STYLE, USER_DIR_PREFIX


def file_read(file_name, *path, encoding="utf-8"):
    """Just a wrapper, since nearly always only read or write are used in this script"""
    if path:
        path = path + (file_name,)
        file_name = join(path[0], *path[1:])
    with open(file_name, encoding=encoding) as ffile:
        return ffile.read()


def file_write(file_name, string, *path, mode="w", encoding="utf-8"):
    """Just a wrapper, since nearly always only read or write are used in this script"""
    if path:
        path = path + (file_name,)
        file_name = join(path[0], *path[1:])
    with open(file_name, mode, encoding=encoding) as ffile:
        ffile.write(string)
    return file_name


class _StringYAML(YAML):
    def dump(self, data, stream=None, **kw):  # pylint: disable=arguments-differ
        as_string = False
        if stream is None:
            as_string = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if as_string:
            return stream.getvalue()


def yaml_load(source, is_string=False):
    """Return a dictionary with the content of the yaml in the source file.
    If a string should be loaded, set is_string to True"""
    yaml = YAML()
    if is_string:
        return yaml.load(source)
    with open(source, encoding="utf-8") as s:
        return yaml.load(s)


def yaml_dump(doc, target=None, transform=None):
    """Dump to the target file. If target is None, return the
    dumped yaml as a String. Otherwise return the path to the file."""
    yaml = _StringYAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    if target is None:
        return yaml.dump(doc, transform=transform)
    with open(target, "w", encoding="utf-8") as f:
        yaml.dump(doc, f, transform=transform)
    return target


def yaml_dump_pandoc_md(doc, target=None):
    """Return the yaml as a pandoc metadata block"""
    return yaml_dump(doc, target, lambda s: f"---\n{s}---\n")


def run_process(args, get_output=False, shell=False):
    """
    Run a process with the given args.
    If get_output is true, return the subprocess.
    """
    args = shlex.split(args) if not shell else args
    name = args[1] if args[0] in ["py", "python", "python3"] else args[0]
    try:
        if get_output:
            pc = subprocess.run(
                args,
                check=True,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding="utf-8",
            )
            return pc
        subprocess.run(args, check=True, shell=shell)
    except subprocess.CalledProcessError:
        logging.error(f"{name} failed!")
        logging.debug(f"{name} command-line:\n{name} {args}!")
        raise
    except FileNotFoundError:
        logging.error(f"{name} not found!")
        raise


def get_full_file_name(path):
    """Return the name and extension of the file in path"""
    _, fname = split(path)
    return fname


def get_file_name(path):
    """Return the name without the extension of the file in path"""
    root, _ = splitext(get_full_file_name(path))
    return root


def get_file_extension(path):
    """Return the extension of the file in path"""
    _, ext = splitext(path)
    return ext[1:]


def has_extension(ffile, extensions):
    """Check if ffile has an extension given in extensions. Extensions can be
    a string or a list of strings."""
    if get_file_extension(ffile) in make_list(extensions):
        return True
    return False


def make_list(item):
    """Make a list with item as its member, if item isn't a list already"""
    return item if isinstance(item, list) else [item]


@contextmanager
def change_dir(new_dir):
    """Changes to the given directory, returns to the current one after"""
    current_dir = getcwd()
    chdir(new_dir)
    yield
    chdir(current_dir)


def get_pack_path(pack):
    for local_path in ["", "./assets", "./styles", "./assets/styles"]:
        pack_path = join(local_path, pack)
        if isdir(pack_path):
            return pack_path.replace("\\", "/")
    return join(CONFIG_DIR, PATH_STYLE, pack).replace("\\", "/")


def expand_directories(item, key=""):
    """
    Look if item is a file in the configuration directory and return the path if
    it is. Searches first for the given path, then looks into a subfolder given by
    key and finally in the "misc" subfolder. If no file is found, just return item.
    """
    if isinstance(item, str) and "@" in item:
        try:
            pack, path = item.split("@")
            pack_path = get_pack_path(pack)
            for folder in ["", key, PATH_MISC]:
                test_file = normpath(join(pack_path, folder, path))
                if isfile(test_file):
                    return test_file.replace("\\", "/")
        except:  # noqa: E722
            pass

    if isinstance(item, str) and USER_DIR_PREFIX in item:
        for folder in ["", key, PATH_MISC]:
            test_file = normpath(item.replace("~", join(CONFIG_DIR, folder)))
            if isfile(test_file):
                return test_file.replace("\\", "/")
    return item
