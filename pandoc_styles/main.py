import logging
import re
import subprocess
import sys
from argparse import ArgumentParser
from copy import deepcopy
from os import getcwd, listdir, mkdir
from os.path import (basename, dirname, isdir, join, normpath, relpath)
from shutil import copy, copytree
from tempfile import TemporaryDirectory
from pkg_resources import resource_filename

import sass
import yaml

from .constants import *  # pylint: disable=W0401, W0614
from .format_mappings import FORMAT_TO_EXTENSION
from .utils import (change_dir, expand_directories, file_read, file_write,
                    has_extension, make_list, run_process)


class PandocStyles:
    """Handles the conversion with styles"""
    def __init__(self, files, formats=None, sfrom="", use_styles=None, metadata="",
                 target="", output_name="", style_file=None):
        self.metadata = metadata
        self.files = files
        self.pandoc_metadata = self.get_pandoc_metadata()
        self.sfrom = sfrom or self.pandoc_metadata.get(MD_FROM_FORMAT)
        self.use_styles = use_styles or self.pandoc_metadata.get(MD_STYLE)
        style_file = style_file or self.pandoc_metadata.get(MD_STYLE_FILE) or STYLE_FILE
        self.styles = yaml.load(file_read(style_file))
        self.target = target or self.pandoc_metadata.get(MD_DESTINATION, "")
        self.output_name = output_name or self.pandoc_metadata.get(MD_OUTPUT_NAME) or \
                           f'{files[0].rpartition(".")[0]}'
        self.formats = formats or make_list(self.pandoc_metadata.get(MD_FORMATS, [])) or \
                       [HTML, PDF]
        self.actual_temp_dir = TemporaryDirectory()
        self.temp_dir = self.actual_temp_dir.name
        self.python_path = ""
        self.do_user_config()

    def run(self):
        """Convert to all given formats"""
        if self.target and not isdir(self.target):
            mkdir(self.target)
        for fmt in self.formats:
            if self.make_format(fmt):
                logging.info(f"Build {fmt}")
            else:
                logging.error(f"Failed to build {fmt}!")

    def make_format(self, fmt):
        """
        Converts to the given format.
        All attributes defined here change with each format
        """
        # initialize attributes
        self.fmt = fmt
        self.to = LATEX if fmt == PDF else fmt
        self.output_file = f"{self.output_name}.{FORMAT_TO_EXTENSION.get(fmt, fmt)}"
        if self.target:
            self.output_file = join(self.target, self.output_file)
        self.cfg = self.get_cfg()

        self.preflight()
        self.process_sass()
        self.add_to_template()
        self.replace_in_template()
        pandoc_args = self.get_pandoc_args()
        logging.debug(f"Command-line args: {pandoc_args}")
        success = run_process(PANDOC_CMD, pandoc_args)
        if success:
            self.replace_in_output()
            self.postflight()
        return success

    def get_pandoc_metadata(self):
        """Get the metadata yaml block in the first source file or given metadata file"""
        ffile = self.metadata or self.files[0]
        md = re.match(r'.?-{3}(.*?)(\n\.{3}\n|\n-{3}\n)',
                      file_read(ffile), flags=re.DOTALL)
        if md:
            return yaml.load(md.group(1))
        logging.warning('No metadata found in the file!')
        return None

    def do_user_config(self):
        """Read the config file and set the options"""
        try:
            config = yaml.load(file_read(CFG_FILE, CONFIG_DIR))
        except FileNotFoundError:
            return
        if config.get(CFG_PANDOC_PATH):
            sys.path.append(normpath(dirname(config[CFG_PANDOC_PATH])))
        if config.get(CFG_PYTHON_PATH):
            self.python_path = normpath(config[CFG_PYTHON_PATH])

    def get_cfg(self):
        """Get the style configuration for the current format"""
        cfg = dict()
        if self.pandoc_metadata is None:
            return cfg

        if self.use_styles:
            start_style = self.styles.get(ALL_STYLE, {})
            start_style[MD_INHERITS] = self.use_styles
            cfg = self.get_styles(start_style)

        # update fields in the cfg with fields in the document metadata, if they exist
        # in the cfg
        for key, val in self.pandoc_metadata.items():
            if key in cfg.get(MD_METADATA, {}):
                cfg_ = cfg[MD_METADATA]
            elif key in cfg.get(MD_CMD_LINE, {}):
                cfg_ = cfg[MD_CMD_LINE]
            else:
                cfg_ = cfg
            self.update_dict(cfg_, {key: val})

        if MD_STYLE_DEF in self.pandoc_metadata:
            self.update_dict(cfg,
                             self.style_to_cfg(self.pandoc_metadata[MD_STYLE_DEF]))

        # add file list and temporary directory, so that preflight scripts can use them
        cfg[MD_CURRENT_FILES] = self.files.copy()
        cfg[MD_TEMP_DIR] = self.temp_dir
        cfg[MD_CFG_DIR] = CONFIG_DIR
        cfg[MD_PANDOC_MD] = self.pandoc_metadata
        return cfg

    def get_styles(self, style):
        """
        Gets the data for all inherited styles
        """
        if not style.get(MD_INHERITS):
            return self.style_to_cfg(style)

        cfg = dict()
        for extra_style in make_list(style[MD_INHERITS]):
            extra_style = self.get_styles(self.styles[extra_style])
            self.update_dict(cfg, extra_style)
        self.update_dict(cfg, self.style_to_cfg(style))
        return cfg

    def get_pandoc_args(self):
        """Build the command line for pandoc out of the given configuration"""
        pandoc_args = [f'-t {self.to} -o "{self.output_file}"']

        if self.sfrom:
            pandoc_args.append(f'--from {self.sfrom}')

        # add pandoc_styles cfg, so that filters can use it
        pandoc_args.append(f'-M {MD_PANDOC_STYLES_MD}="{self.make_cfg_file()}"')

        complex_data = {}
        for group, prefix in [(MD_CMD_LINE, "--"), (MD_METADATA, "-V ")]:
            if group in self.cfg:
                for key, value in self.cfg[group].items():
                    for item in make_list(value):
                        if not item:
                            continue
                        elif item is True:
                            pandoc_args.append(f'{prefix}{key}')
                        elif isinstance(item, dict):
                            complex_data[key] = value
                            break
                        else:
                            item = expand_directories(item, key)
                            pandoc_args.append(f'{prefix}{key}="{item}"')

        for ffile in self.cfg[MD_CURRENT_FILES]:
            pandoc_args.append(f'"{ffile}"')

        if self.metadata:
            pandoc_args.append(f'"{self.metadata}"')

        if complex_data:
            complex_data = f'---\n{yaml.dump(complex_data)}\n...\n'
            complex_data = file_write("cur_metadata.yaml", complex_data, self.temp_dir)
            pandoc_args.append(f'"{complex_data}"')
        return " ".join(pandoc_args)

    def preflight(self):
        """Run all preflight scripts given in the style definition"""
        if MD_PREFLIGHT not in self.cfg:
            return
        self.cfg[MD_CURRENT_FILES] = [copy(f, self.temp_dir)
                                      for f in self.cfg[MD_CURRENT_FILES]]
        for script in make_list(self.cfg[MD_PREFLIGHT]):
            script = expand_directories(script, MD_PREFLIGHT)
            if self.python_path and has_extension(script, "py"):
                script = f'{self.python_path} "{script}"'
            cfg = self.make_cfg_file()
            run_process(script, f'--cfg "{cfg}" --fmt {self.fmt}')
            self.read_cfg_file()

    def postflight(self):
        """Run all postflight scripts given in the style definition"""
        if MD_POSTFLIGHT not in self.cfg:
            return
        cfg = self.make_cfg_file()
        for script in make_list(self.cfg[MD_POSTFLIGHT]):
            script = expand_directories(script, MD_POSTFLIGHT)
            if self.python_path and has_extension(script, "py"):
                script = f'{self.python_path} "{script}"'
            run_process(script, f'"{self.output_file}" --cfg "{cfg}" '
                        f'--fmt {self.fmt}')

    def process_sass(self):
        """Build the css out of the sass informations given in the style definition"""
        if MD_SASS not in self.cfg:
            return

        css = [f'${var}: {str(val).lower() if isinstance(val, bool) else str(val)};'
               for var, val in self.cfg[MD_SASS].get(MD_SASS_VARS, {}).items()]
        sass_files = make_list(self.cfg[MD_SASS][MD_SASS_FILES])
        css_name = f"{basename(sass_files[0]).rpartition('.')[0]}.{CSS}"
        css.extend([file_read(expand_directories(f, MD_SASS)) for f in sass_files])
        css.extend(make_list(self.cfg[MD_SASS].get(MD_SASS_APPEND, [])))
        css = "\n".join(css)
        css = sass.compile(string=css, output_style='expanded',
                           include_paths=[join(CONFIG_DIR, PATH_SASS)])

        css_file_path = self.cfg[MD_SASS].get(MD_SASS_OUTPUT_PATH)
        if css_file_path == PATH_TEMP:
            css_file_path = self.temp_dir
        elif css_file_path == USER_DIR_PREFIX:
            css_file_path = join(CONFIG_DIR, PATH_CSS)
        elif css_file_path:
            css_file_path = join(self.target, css_file_path)
        else:
            css_file_path = self.target if self.target else "."
        if not isdir(css_file_path):
            mkdir(css_file_path)
        css_file_path = file_write(css_name, css, css_file_path)
        try:
            css_file_path = relpath(css_file_path, self.target).replace("\\", "/")
        except ValueError:
            pass
        self.update_dict(self.cfg, {MD_CMD_LINE: {CSS: [css_file_path]}})

    def add_to_template(self):
        """Add code to the template given in the style definition"""
        if MD_ADD_TO_TEMPLATE not in self.cfg:
            return
        self.modify_template(
            r'(\$for\(header-includes\)\$\n\$header-includes\$\n\$endfor\$)',
            self.cfg[MD_ADD_TO_TEMPLATE], True)

    def replace_in_template(self):
        """Replace code in the template with other code given in the style definition"""
        if MD_REPL_IN_TEMPLATE not in self.cfg:
            return
        for item in make_list(self.cfg[MD_REPL_IN_TEMPLATE]):
            self.modify_template(item[MD_REPL_PATTERN], item.get(MD_REPL_TEXT, ""),
                                 item.get(MD_REPL_ADD, False), item.get(MD_REPL_COUNT, 0))

    def modify_template(self, pattern, repl, add=False, count=0):
        """Helper method to do the actual replacement"""
        try:
            template = file_read(self.cfg[MD_CMD_LINE][MD_TEMPLATE])
        except (KeyError, FileNotFoundError):
            try:
                template = subprocess.run(f'{PANDOC_CMD} -D {self.to}',
                                          stdout=subprocess.PIPE, encoding="utf-8",
                                          check=True)
                template = template.stdout
            except (subprocess.CalledProcessError, FileNotFoundError):
                return
        original_template = template
        template = self.replace_in_text(pattern, repl, template, add, count)
        if original_template != template:
            template = file_write("new.template", template, self.temp_dir)
            self.update_dict(self.cfg, {MD_CMD_LINE: {MD_TEMPLATE: template}})

    def replace_in_output(self):
        """Replace text in the output with text given in the style definition"""
        if MD_REPL_IN_OUTPUT not in self.cfg:
            return
        original_text = text = file_read(self.output_file)
        for item in self.cfg[MD_REPL_IN_OUTPUT]:
            text = self.replace_in_text(item[MD_REPL_PATTERN], item.get(MD_REPL_TEXT, ""),
                                        text, item.get(MD_REPL_ADD), item.get(MD_REPL_COUNT, 0))
        if original_text != text:
            file_write(self.output_file, text)

    def replace_in_text(self, pattern, repl, text, add=False, count=0):
        """Helper method to replace text"""
        repl = "\n".join(item for item in make_list(repl))
        repl = repl.replace("\\", '\\\\')
        repl = fr"{repl}\n\1" if add else repl
        text = re.sub(pattern, repl, text, count, re.DOTALL)
        return text

    def style_to_cfg(self, style):
        """Transform a style to the configuration for the current format"""
        cfg = dict()
        for group in [ALL_FMTS, self.fmt]:
            if group in style:
                self.update_dict(cfg, style[group])
        return cfg

    def update_dict(self, dictionary, new):
        """
        Merge dictionary with new. Single keys are replaces, but nested dictionaries
        and list are appended
        """
        # we deepcopy new, so that it stays independent from our dictionary
        new = deepcopy(new)
        for key, value in new.items():
            if not dictionary.get(key):
                dictionary[key] = value
            elif isinstance(value, dict):
                self.update_dict(dictionary[key], value)
            elif isinstance(value, list) and isinstance(dictionary[key], list):
                dictionary[key].extend(value)
            else:
                dictionary[key] = value

    def make_cfg_file(self):
        """
        Dump the configuration for a format into a file. This way filter and flight
        scripts can read the configuration.
        """
        return file_write(CFG_TEMP_FILE, yaml.dump(self.cfg), self.temp_dir)

    def read_cfg_file(self):
        """Read the cfg file"""
        self.cfg = yaml.load(file_read(CFG_TEMP_FILE, self.temp_dir))


def main():
    """Parse the command line arguments and run PnadocStyles with the given args"""
    parser = ArgumentParser(description="Runs pandoc with options defined in styles")
    parser.add_argument('files', nargs='*', default=None,
                        help='The source files to be converted')
    parser.add_argument('-f', '--folder', nargs='?', const=True, default=None,
                        help='All files in the folder are converted together.')
    parser.add_argument('--extensions', nargs='*', default=["md", "markdown"],
                        help='If the folder option is used, only convert files '
                             'with the given extensions.')
    parser.add_argument('-t', '--to', nargs='*', default=[],
                        help='The formats that should be produced.')
    parser.add_argument('--from-format', nargs='?', default="",
                        help='The format of the source files.')
    parser.add_argument('-d', '--destination', nargs='?', default="",
                        help='The target folder')
    parser.add_argument('-o', '--output-name', nargs='?', default="",
                        help='The name of the output file without an extension. '
                             'Defaults to the name of the first input file.')
    parser.add_argument('-s', '--styles', nargs='*', default=[],
                        help='Styles to use for the conversion.')
    parser.add_argument('--style-file', nargs='?', default=None,
                        help='Path to the style file that should be used. '
                             'Defaults to the style file in the configuration folder.')
    parser.add_argument('-m', '--metadata', nargs='?', default=None,
                        help='Path to the metadata file that should be used.')
    parser.add_argument('-w', '--working-dir', nargs='?', default=getcwd(),
                        help='The folder of the source files, for use in macros etc.')
    parser.add_argument('--init', action='store_true',
                        help='Create the user configuration folder')
    parser.add_argument('--log', nargs='?', default="INFO",
                        choices=["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"],
                        help='The logging level. '
                             'Defaults to "INFO"')
    args = parser.parse_args()

    # logging
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=getattr(logging, args.log))

    # initialize config directory
    if args.init:
        if not isdir(CONFIG_DIR):
            copytree(resource_filename(MODULE_NAME, 'config_dir'), CONFIG_DIR)
            logging.info("Created configuration directory: user/pandoc_styles!")
        return

    if args.folder:
        if args.folder is True:
            args.folder = getcwd()
        args.files = [f for f in listdir(args.folder)
                      if has_extension(f, args.extensions)]
        args.files.sort()

    if not args.files:
        parser.print_help()
        return

    with change_dir(args.working_dir):
        PandocStyles(args.files, args.to, args.from_format, args.styles, args.metadata,
                     args.destination, args.output_name, args.style_file).run()


if __name__ == '__main__':
    main()
