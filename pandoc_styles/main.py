import logging
import re
import subprocess
import sys
from argparse import ArgumentParser
from copy import deepcopy
from os import getcwd, listdir, mkdir
from os.path import dirname, expanduser, isfile, join, normpath, isdir, basename, relpath
from shutil import copy
from tempfile import TemporaryDirectory
import yaml
import sass
from .format_mappings import FORMAT_TO_EXTENSION
from .utils import (change_dir, file_read, file_write, has_extension,
                    make_list, run_process)


class PandocStyles:
    """Handles the conversion with styles"""
    def __init__(self, files, formats=None, sfrom="", styles=None, metadata="",
                 target="", output_name=""):
        self.files = files
        self.metadata = metadata
        self.target = target
        self.sfrom = sfrom
        self.output_name = f'{files[0].rpartition(".")[0]}' if not output_name \
                           else output_name
        self.config_dir = join(expanduser("~"), "pandoc_styles")
        if styles:
            self.styles = yaml.load(file_read(styles))
        else:
            self.styles = yaml.load(file_read("styles.yaml", self.config_dir))
        self.yaml_block = self.get_yaml_block()
        if formats:
            self.formats = formats
        elif "formats" in self.yaml_block:
            self.formats = make_list(self.yaml_block["formats"])
        else:
            self.formats = ["pdf", "html"]
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
        self.to = "latex" if fmt == "pdf" else fmt
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
        success = run_process("pandoc", pandoc_args)
        if success:
            self.replace_in_output()
            self.postflight()
        return success

    def get_yaml_block(self):
        """Get the metadata yaml block in the first source file or given metadata file"""
        ffile = self.metadata if self.metadata else self.files[0]
        md = re.match(r'.?-{3}(.*?)(\n\.{3}\n|\n-{3}\n)',
                      file_read(ffile), flags=re.DOTALL)
        if md:
            return yaml.load(md.group(1))
        logging.warning('No metadata found in the file!')
        return None

    def do_user_config(self):
        """Read the config file and set the options"""
        try:
            config = yaml.load(file_read("config.yaml", self.config_dir))
        except FileNotFoundError:
            return
        if  config.get("pandoc-path"):
            sys.path.append(normpath(dirname(config["pandoc-path"])))
        if  config.get("python-path"):
            self.python_path = normpath(config["python-path"])

    def get_cfg(self):
        """Get the style configuration for the current format"""
        cfg = dict()
        if self.yaml_block is None:
            return cfg

        if "style" in self.yaml_block:
            start_style = self.styles.get("All", {})
            start_style["inherits"] = self.yaml_block["style"]
            cfg = self.get_styles(start_style)

        if "style-definition" in self.yaml_block:
            self.update_dict(cfg, self.style_to_cfg(self.yaml_block["style-definition"]))

        # add file list and temporary directory, so that preflight scripts can use them
        cfg["current-files"] = self.files.copy()
        cfg["temp-dir"] = self.temp_dir
        cfg["config-dir"] = self.config_dir
        return cfg

    def get_styles(self, style):
        """
        Gets the data for all inherited styles
        """
        if "inherits" not in style:
            return self.style_to_cfg(style)

        cfg = dict()
        for extra_style in make_list(style["inherits"]):
            extra_style = self.get_styles(self.styles[extra_style])
            self.update_dict(cfg, extra_style)
        self.update_dict(cfg, self.style_to_cfg(style))
        return cfg

    def get_pandoc_args(self):
        """Build the command line for pandoc out of the given configuration"""
        pandoc_args = [f'-t {self.to} -o "{self.output_file}"']

        for ffile in self.cfg["current-files"]:
            pandoc_args.append(f'"{ffile}"')

        if self.sfrom:
            pandoc_args.append(f'--from {self.sfrom}')
        if self.metadata:
            pandoc_args.append(f'"{self.metadata}"')

        # add pandoc_styles cfg, so that filters can use it
        pandoc_args.append(f'-M pandoc_styles_="{self.make_cfg_file()}"')

        for group, prefix in [("command-line", "--"), ("metadata", "-V ")]:
            if group in self.cfg:
                for key, value in self.cfg[group].items():
                    for item in make_list(value):
                        if not item:
                            continue
                        elif item is True:
                            pandoc_args.append(f'{prefix}{key}')
                        else:
                            item = self.expand_directories(item, key)
                            pandoc_args.append(f'{prefix}{key}="{item}"')
        return " ".join(pandoc_args)

    def preflight(self):
        """Run all preflight scripts given in the style definition"""
        if "preflight" not in self.cfg:
            return
        self.cfg["current-files"] = [copy(f, self.temp_dir)
                                     for f in self.cfg["current-files"]]
        for script in make_list(self.cfg["preflight"]):
            script = self.expand_directories(script, "preflight")
            if self.python_path and has_extension(script, "py"):
                script = f'{self.python_path} "{script}"'
            cfg = self.make_cfg_file()
            run_process(script, f'--cfg "{cfg}" --fmt {self.fmt}')
            self.read_cfg_file()

    def postflight(self):
        """Run all postflight scripts given in the style definition"""
        if "postflight" not in self.cfg:
            return
        cfg = self.make_cfg_file()
        for script in make_list(self.cfg["postflight"]):
            script = self.expand_directories(script, "postflight")
            if self.python_path and has_extension(script, "py"):
                script = f'{self.python_path} "{script}"'
            run_process(script, f'"{self.output_file}" --cfg "{cfg}" '
                        f'--fmt {self.fmt}')

    def process_sass(self):
        """Build the css out of the sass informations given in the style definition"""
        if "sass" not in self.cfg:
            return

        css = [f'${var}: {str(val).lower() if isinstance(val, bool) else str(val)};'
               for var, val in self.cfg["sass"].get("variables", {}).items()]
        sass_files = make_list(self.cfg["sass"]["files"])
        css_name = f"{basename(sass_files[0]).rpartition('.')[0]}.css"
        css.extend([file_read(self.expand_directories(f, "sass")) for f in sass_files])
        css.extend(make_list(self.cfg["sass"].get("append", [])))
        css = "\n".join(css)
        css = sass.compile(string=css, output_style='expanded',
                           include_paths=[join(self.config_dir, "sass")])

        css_file_path = self.cfg["sass"].get("output-path")
        if css_file_path == "temp":
            css_file_path = self.temp_dir
        elif css_file_path == "~/":
            css_file_path = join(self.config_dir, "css")
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

        if "metadata" not in self.cfg:
            self.cfg["metadata"] = dict()
        self.update_dict(self.cfg["metadata"], {"css": [css_file_path]})

    def add_to_template(self):
        """Add code to the template given in the style definition"""
        if "add-to-template" not in self.cfg:
            return
        self.modify_template(
            r'(\$for\(header-includes\)\$\n\$header-includes\$\n\$endfor\$)',
            self.cfg["add-to-template"], True)

    def replace_in_template(self):
        """Replace code in the template with other code given in the style definition"""
        if "replace-in-template" not in self.cfg:
            return
        for item in make_list(self.cfg["replace-in-template"]):
            self.modify_template(item["pattern"], item.get("replacement-text", ""),
                                 item.get("add", False), item.get("count", 0))

    def modify_template(self, pattern, repl, add=False, count=0):
        """Helper method to do the actual replacement"""
        try:
            template = file_read(self.cfg["command-line"]["template"])
        except (KeyError, FileNotFoundError):
            try:
                template = subprocess.run(f'pandoc -D {self.to}',
                                          stdout=subprocess.PIPE, encoding="utf-8",
                                          check=True)
                template = template.stdout
            except (subprocess.CalledProcessError, FileNotFoundError):
                return
        original_template = template
        template = self.replace_in_text(pattern, repl, template, add, count)
        if original_template != template:
            template = file_write("new.template", template, self.temp_dir)
            if "command-line" not in self.cfg:
                self.cfg["command-line"] = dict()
            self.cfg["command-line"]["template"] = template

    def replace_in_output(self):
        """Replace text in the output with text given in the style definition"""
        if "replace-in-output" not in self.cfg:
            return
        original_text = text = file_read(f"{self.output_name}.{self.fmt}")
        for item in self.cfg["replace-in-output"]:
            text = self.replace_in_text(item["pattern"], item.get("replacement-text", ""),
                                        text, item.get("add"), item.get("count", 0))
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
        for group in ["all", self.fmt]:
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
            if key not in dictionary:
                dictionary[key] = value
            elif isinstance(value, dict):
                self.update_dict(dictionary[key], value)
            elif isinstance(value, list) and isinstance(dictionary[key], list):
                dictionary[key].extend(value)
            else:
                dictionary[key] = value

    def expand_directories(self, item, key=""):
        """
        Look if item is a file in the configuration directory and return the path if
        it is. Searches first for the given path, then looks into a subfolder given by
        key and finally in the "misc" subfolder. If no file is found, just return item.
        """
        if isinstance(item, str) and "~/" in item:
            for folder in ["", key, "misc"]:
                test_file = normpath(item.replace("~", join(self.config_dir, folder)))
                if isfile(test_file):
                    return test_file
        return item

    def make_cfg_file(self):
        """
        Dump the configuration for a format into a file. This way filter and flight
        scripts can read the configuration.
        """
        return file_write("cfg.yaml", yaml.dump(self.cfg), self.temp_dir)

    def read_cfg_file(self):
        """Read the cfg file"""
        self.cfg = yaml.load(file_read("cfg.yaml", self.temp_dir))


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
    parser.add_argument('-s', '--styles', nargs='?', default=None,
                        help='Path to the style file that should be used. '
                             'Defaults to the style file on the configuration folder.')
    parser.add_argument('-m', '--metadata', nargs='?', default=None,
                        help='Path to the metadata file that should be used.')
    parser.add_argument('-w', '--working-dir', nargs='?', default=getcwd(),
                        help='The folder of the source files, for use in macros etc.')
    parser.add_argument('--log', nargs='?', default="INFO",
                        choices=["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"],
                        help='The logging level. '
                             'Defaults to "INFO"')
    args = parser.parse_args()

    # logging
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=getattr(logging, args.log))

    if args.folder:
        if args.folder is True:
            args.folder = getcwd()
        args.files = [f for f in listdir(args.folder)
                      if has_extension(f, args.extensions)]
        args.files.sort()

    with change_dir(args.working_dir):
        PandocStyles(args.files, args.to, args.from_format, args.styles, args.metadata,
                     args.destination, args.output_name).run()


if __name__ == '__main__':
    main()
