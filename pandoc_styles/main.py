# ruff: noqa: F405

import logging
import re
import sys
from argparse import ArgumentParser
from copy import deepcopy
from os import getcwd, listdir, mkdir, remove
from os.path import dirname, isdir, isfile, join, normpath, relpath
from shutil import copy, copytree
from tempfile import TemporaryDirectory

import sass
from pkg_resources import resource_filename

from .constants import *  # noqa: F403
from .format_mappings import FORMAT_TO_EXTENSION
from .pandoc_cmd_line_options import COMMAND_LINE_OPTIONS
from .utils import (
    change_dir,
    expand_directories,
    file_read,
    file_write,
    get_file_name,
    get_full_file_name,
    get_pack_path,
    has_extension,
    make_list,
    run_process,
    yaml_dump,
    yaml_dump_pandoc_md,
    yaml_load,
)


class PandocStyles:
    """Handles the conversion with styles"""

    def __init__(
        self,
        files,
        formats=None,
        from_format="",
        use_styles=None,
        add_styles=None,
        metadata="",
        target="",
        output_name="",
        stylepacks=None,
        style_file=None,
        quiet=False,
        to_file_type=None,
    ):
        self.actual_temp_dir = TemporaryDirectory()
        self.temp_dir = self.actual_temp_dir.name
        self.metadata = metadata
        self.pandoc_metadata, files = self.get_pandoc_metadata(
            metadata or files[0], files
        )
        self.files = self.pandoc_metadata.get(MD_FILE_LIST) or [
            f for f in files if f not in self.pandoc_metadata.get(MD_EXCLUDED_FILES, [])
        ]
        self.quiet = quiet
        self.from_format = from_format or self.pandoc_metadata.get(MD_FROM_FORMAT)
        self.formats = (
            formats
            or make_list(self.pandoc_metadata.get(MD_FORMATS, []))
            or [HTML, PDF]
        )
        self.use_styles = use_styles or make_list(
            self.pandoc_metadata.get(MD_STYLE, [])
        )
        style_file = style_file or self.pandoc_metadata.get(MD_STYLE_FILE) or STYLE_FILE
        self.stylepacks = stylepacks or make_list(
            self.pandoc_metadata.get(MD_STYLE_PACKS, [])
        )
        self.used_stylepacks = []
        self.use_styles.extend(add_styles or [])
        self.styles = yaml_load(style_file)
        self.style = self.build_style()
        self.target = target or self.pandoc_metadata.get(MD_DESTINATION, "")
        self.output_name = (
            output_name
            or self.pandoc_metadata.get(MD_OUTPUT_NAME)
            or get_file_name(files[0])
        )
        self.output_ext = to_file_type
        self.python_path = "python"
        self._do_user_config()

    def run(self):
        """Convert to all given formats"""
        if self.target and not isdir(self.target):
            mkdir(self.target)
        for fmt in self.formats:
            self.make_format(fmt)

    def get_output(self, fmt):
        """
        Converts to the given format and returns the output.
        """
        self.quiet = True
        self.target = self.temp_dir
        self.make_format(fmt)
        return file_read(self.cfg[OUTPUT_FILE])

    def print_output(self, fmt):
        """
        Converts to the given format and prints the output.
        """
        print(self.get_output(fmt))

    def build_style(self):
        style = {}
        if self.stylepacks:
            style = self._get_stylepack_style(style, self.stylepacks)

        if self.use_styles:
            style[MD_INHERITS] = self.use_styles
            style = self._get_style(style, self.styles)

        if MD_STYLE_DEF in self.pandoc_metadata:
            self.update_dict(
                style, self._get_style(self.pandoc_metadata[MD_STYLE_DEF], self.styles)
            )

        all_style = self.styles.get(ALL_STYLE)
        if all_style:
            all_style = self._get_style({MD_INHERITS: ALL_STYLE}, self.styles)
            self.update_dict(all_style, style)
            return all_style
        return style

    def _get_stylepack_style(self, style, stylepacks):
        if not stylepacks:
            return style

        for stylepack in make_list(stylepacks):
            if isinstance(stylepack, str):
                used_styles = [DEFAULT_STYLE]
                pack = stylepack
            else:
                for k, v in stylepack.items():
                    pack = k
                    used_styles = make_list(v)

            pack_path = get_pack_path(pack)
            self.used_stylepacks.append(pack)
            stylepack_styles = yaml_load(join(pack_path, f"{pack}.yaml"))

            if stylepack_styles.get(ALL_STYLE):
                used_styles.insert(0, ALL_STYLE)

            for s in used_styles:
                self.update_dict(
                    style, self._get_style(stylepack_styles[s], stylepack_styles)
                )
        return style

    def _get_style(self, style, all_styles):
        """
        Gets the data for all inherited styles
        """
        stylepacks = style.get(MD_STYLE_PACKS)
        inherited = deepcopy(make_list(style.get(MD_INHERITS, [])))
        if not inherited and not stylepacks:
            return style

        if stylepacks:
            style = self._get_stylepack_style(style, stylepacks)
        new_style = dict()
        if inherited:
            del style[MD_INHERITS]
            for extra_style in inherited:
                extra_style = self._get_style(all_styles[extra_style], all_styles)
                self.update_dict(new_style, extra_style)
        self.update_dict(new_style, style)
        return new_style

    def make_format(self, fmt):
        """
        Converts to the given format.
        All attributes defined here change with each format
        """
        self.cfg = self._get_cfg(fmt)
        self._preflight()
        self._process_sass()
        self._add_to_template()
        self._replace_in_template()
        pandoc_args = self._get_pandoc_args()
        logging.debug(f"Command-line args: {pandoc_args}")
        try:
            run_process(pandoc_args, self.quiet)
            self._replace_in_output()
            self._postflight()
            logging.info(f"Build {self.cfg[OUTPUT_FILE]}")
        except:  # noqa: E722
            logging.error(f"Failed to build {self.cfg[OUTPUT_FILE]}!")
            sys.exit(1)

    def get_pandoc_metadata(self, md_file, files):
        """Get the metadata yaml block in the file given"""
        if not md_file:
            return {}

        if has_extension(md_file, ["yaml", "yml"]):
            return yaml_load(md_file)

        text = file_read(md_file)
        md = re.match(r".?-{3}(.*?)(\n\.{3}\n|\n-{3}\n)", text, flags=re.DOTALL)
        if not md:
            return {}, files
        md = md.group(1)
        # remove md from the file, since it is no longer needed and would overwrite
        # metadata fields in the wrong way
        text = re.sub(r".?-{3}(.*?)(\n\.{3}\n|\n-{3}\n)", "", text, flags=re.DOTALL)
        files[0] = file_write(get_full_file_name(md_file), text, self.temp_dir)
        return yaml_load(md, True), files

    def _do_user_config(self):
        """Read the config file and set the options"""
        try:
            config = yaml_load(join(CONFIG_DIR, CFG_FILE))
        except FileNotFoundError:
            logging.warning(
                "No configuration file found! Please initialize "
                "pandoc_styles with: pandoc_styles --init"
            )
            return
        if config.get(CFG_PANDOC_PATH):
            sys.path.append(normpath(dirname(config[CFG_PANDOC_PATH])))
        if config.get(CFG_PYTHON_PATH):
            self.python_path = normpath(config[CFG_PYTHON_PATH])

    def _get_cfg(self, fmt):
        """Get the style configuration for the current format"""
        cfg = self.style_to_cfg(self.style, fmt)
        # update fields in the cfg with fields in the document metadata
        self.update_dict(cfg, self.pandoc_metadata)

        if MD_VERBATIM_VARIABLES not in cfg:
            cfg[MD_VERBATIM_VARIABLES] = {}
        # add all needed infos to cfg
        cfg[MD_CURRENT_FILES] = self.files.copy()
        ext = self.output_ext if self.output_ext else FORMAT_TO_EXTENSION.get(fmt, fmt)
        cfg[OUTPUT_FILE] = f"{self.output_name}.{ext}"
        if self.target:
            cfg[OUTPUT_FILE] = join(self.target, cfg[OUTPUT_FILE])
        cfg[FMT] = fmt
        cfg[TO_FMT] = fmt
        if cfg["pdf-engine"] in [
            "pdflatex",
            "xelatex",
            "lualatex",
            "tectonic",
            "latexmk",
        ] or (not cfg["pdf-engine"] and fmt == PDF):
            cfg[TO_FMT] = LATEX
        cfg[MD_TEMP_DIR] = self.temp_dir
        cfg[MD_CFG_DIR] = CONFIG_DIR
        cfg[MD_STYLE_PACKS] = self.used_stylepacks
        for stylepack in cfg[MD_STYLE_PACKS]:
            cfg[MD_VERBATIM_VARIABLES][f"{stylepack}-dir"] = get_pack_path(stylepack)

        # add some infos to the verbatim variables
        cfg[MD_VERBATIM_VARIABLES][MD_CFG_DIR] = cfg[MD_CFG_DIR]
        cfg[MD_VERBATIM_VARIABLES][MD_TEMP_DIR] = cfg[MD_TEMP_DIR]
        cfg[MD_VERBATIM_VARIABLES][OUTPUT_FILE] = cfg[OUTPUT_FILE]
        return cfg

    def _get_pandoc_args(self):
        """Build the command line for pandoc out of the given configuration"""
        pandoc_args = [
            f'{PANDOC_CMD} -t {self.cfg[TO_FMT]} -o "{self.cfg[OUTPUT_FILE]}"'
        ]

        if self.from_format:
            pandoc_args.append(f"--read {self.from_format}")

        # add pandoc_styles cfg, so that filters can use it
        pandoc_args.append(f'-M {MD_PANDOC_STYLES_MD}="{self._make_cfg_file()}"')

        # filter out command-line options
        keys_to_delete = []
        for key, value in self.cfg.items():
            if key not in COMMAND_LINE_OPTIONS:
                continue
            keys_to_delete.append(key)
            if key == "filter":
                for item in make_list(value):
                    if item.endswith(".lua"):
                        key = "lua-filter"
                    else:
                        key = "filter"
                    item = self.expand_dirs(item, key)
                    pandoc_args.append(f"--{key}={item}")
                continue
            for item in make_list(value):
                if not item:
                    continue
                elif item is True:
                    pandoc_args.append(f"--{key}")
                else:
                    item = self.expand_dirs(item, key)
                    pandoc_args.append(f'--{key}="{item}"')

        # add verbatim variables
        for key, value in self.cfg[MD_VERBATIM_VARIABLES].items():
            pandoc_args.append(f'-V {key}="{value}"')
        keys_to_delete.append(MD_VERBATIM_VARIABLES)

        # add expandable metadata that can be overridden in the document
        if MD_EXPANDABLE_VARIABLES in self.cfg:
            for key, value in self.cfg[MD_EXPANDABLE_VARIABLES].items():
                if not self.cfg.get(key, False):
                    pandoc_args.append(f'-V {key}="{self.expand_dirs(value, key)}"')
            keys_to_delete.append(MD_EXPANDABLE_VARIABLES)

        for key in keys_to_delete:
            del self.cfg[key]

        # compatibility with older versions
        complex_data = {}
        for group, prefix in [
            ("command-line", "--"),
            ("metadata", "-M "),
            ("template-variables", "-V "),
        ]:
            if group not in self.cfg:
                continue
            for key, value in self.cfg[group].items():
                for item in make_list(value):
                    if not item:
                        continue
                    elif item is True:
                        pandoc_args.append(f"{prefix}{key}")
                    elif isinstance(item, dict):
                        complex_data[key] = value
                        break
                    else:
                        item = self.expand_dirs(item, key)
                        pandoc_args.append(f'{prefix}{key}="{item}"')
            del self.cfg[group]
        if complex_data:
            complex_data = yaml_dump_pandoc_md(
                complex_data, join(self.temp_dir, "cmplx_metadata.yaml")
            )
            pandoc_args.append(f'"{complex_data}"')
        # -----------------------------------------------

        for ffile in self.cfg[MD_CURRENT_FILES]:
            pandoc_args.append(f'"{ffile}"')

        if self.metadata:
            pandoc_args.append(f'"{self.metadata}"')
        meta = yaml_dump_pandoc_md(self.cfg, join(self.temp_dir, "cur_metadata.yaml"))
        pandoc_args.append(f'"{meta}"')
        return " ".join(pandoc_args)

    def _flight(self, flight_type, repl_txt, repl_val):
        """Run a flight script"""
        if flight_type not in self.cfg:
            return
        for script in make_list(self.cfg[flight_type]):
            if len(script.split(" ")) == 1 and has_extension(script, "py"):
                cfg = self._make_cfg_file()
                script = self.expand_dirs(script, flight_type)
                if self.python_path:
                    script = f'{self.python_path} "{script}" '
                run_process(f'{script} --cfg "{cfg}"')
                self._read_cfg_file()
            else:
                script = script.replace(repl_txt, repl_val)
                run_process(script)

    def _preflight(self):
        """Run all _preflight scripts given in the style definition"""
        if MD_PREFLIGHT not in self.cfg:
            return
        new = []
        if not isdir(join(self.temp_dir, MODIFIED_FILES)):
            mkdir(join(self.temp_dir, MODIFIED_FILES))
        for f in self.cfg[MD_CURRENT_FILES]:
            modified_file = join(self.temp_dir, MODIFIED_FILES, get_full_file_name(f))
            if isfile(modified_file):
                remove(modified_file)
            new.append(copy(f, modified_file))
        self.cfg[MD_CURRENT_FILES] = new
        self._flight(
            MD_PREFLIGHT,
            "<files>",
            " ".join(f'"{x}"' for x in self.cfg[MD_CURRENT_FILES]),
        )

    def _postflight(self):
        """Run all _postflight scripts given in the style definition"""
        self._flight(MD_POSTFLIGHT, "<file>", f'"{self.cfg[OUTPUT_FILE]}"')

    def _process_sass(self):
        """Build the css out of the sass informations given in the style definition"""
        if MD_SASS not in self.cfg:
            return

        cfg = self.cfg[MD_SASS]
        sass_files = make_list(cfg[MD_SASS_FILES])
        css_name = f'{cfg.get(MD_SASS_NAME, "stylesheet")}.{CSS}'
        css = [
            f"${var}: {str(val).lower() if isinstance(val, bool) else str(val)};"
            for var, val in cfg.get(MD_SASS_VARS, {}).items()
        ]
        css.extend([file_read(self.expand_dirs(f, MD_SASS)) for f in sass_files])
        css.extend(make_list(cfg.get(MD_SASS_APPEND, [])))
        css = sass.compile(
            string="\n".join(css),
            output_style="expanded",
            include_paths=[join(CONFIG_DIR, PATH_SASS)],
        )

        css_file_path = cfg.get(MD_SASS_OUTPUT_PATH)
        temp = css_file_path == PATH_TEMP
        if temp:
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
        if not temp:
            try:
                css_file_path = relpath(css_file_path, self.target).replace("\\", "/")
            except ValueError:
                pass
        self.update_dict(self.cfg, {CSS: [css_file_path]})

    def _add_to_template(self):
        """Add code to the template given in the style definition"""
        if MD_ADD_TO_TEMPLATE not in self.cfg:
            return
        for item in make_list(self.cfg[MD_ADD_TO_TEMPLATE]):
            self._modify_template(
                r"(\$for\(header-includes\)\$\n\$header-includes\$\n\$endfor\$)",
                item,
                True,
            )

    def _replace_in_template(self):
        """Replace code in the template with other code given in the style definition"""
        if MD_REPL_IN_TEMPLATE not in self.cfg:
            return
        for item in make_list(self.cfg[MD_REPL_IN_TEMPLATE]):
            self._modify_template(
                item[MD_REPL_PATTERN],
                item.get(MD_REPL_TEXT, ""),
                item.get(MD_REPL_ADD, False),
                item.get(MD_REPL_COUNT, 0),
            )

    def _modify_template(self, pattern, repl, add=False, count=0):
        """Helper method to do the actual replacement"""
        try:
            template = file_read(self.expand_dirs(self.cfg[MD_TEMPLATE], MD_TEMPLATE))
        except (KeyError, FileNotFoundError):
            pc = run_process(f"{PANDOC_CMD} -D {self.cfg[TO_FMT]}", True)
            if not pc:
                return
            template = pc.stdout
        original_template = template
        if isfile(self.expand_dirs(repl, MD_TEMPLATE)):
            repl = file_read(self.expand_dirs(repl, MD_TEMPLATE))
        template = self._replace_in_text(pattern, repl, template, add, count)
        if original_template != template:
            template = file_write("new.template", template, self.temp_dir)
            self.cfg[MD_TEMPLATE] = template
        # for html we need the styles.html file in addition
        if self.cfg[TO_FMT] == HTML:
            pc = run_process(
                f"{PANDOC_CMD} --print-default-data-file=templates/styles.html", True
            )
            if pc:
                file_write("styles.html", pc.stdout, self.temp_dir)

    def _replace_in_output(self):
        """Replace text in the output with text given in the style definition"""
        if MD_REPL_IN_OUTPUT not in self.cfg:
            return
        original_text = text = file_read(self.cfg[OUTPUT_FILE])
        for item in self.cfg[MD_REPL_IN_OUTPUT]:
            text = self._replace_in_text(
                item[MD_REPL_PATTERN],
                item.get(MD_REPL_TEXT, ""),
                text,
                item.get(MD_REPL_ADD),
                item.get(MD_REPL_COUNT, 0),
            )
        if original_text != text:
            file_write(self.cfg[OUTPUT_FILE], text)

    @staticmethod
    def _replace_in_text(pattern, repl, text, add=False, count=0):
        """Helper method to replace text"""
        repl = "\n".join(item for item in make_list(repl))
        repl = repl.replace("\\", "\\\\")
        repl = rf"{repl}\n\1" if add else repl
        text = re.sub(pattern, repl, text, count, re.DOTALL)
        return text

    @classmethod
    def style_to_cfg(cls, style, fmt):
        """Transform a style to the configuration for the current format"""
        cfg = dict()
        for group in [ALL_FMTS, fmt]:
            if group in style:
                cls.update_dict(cfg, style[group])
        return cfg

    @classmethod
    def update_dict(cls, dictionary, new):
        """
        Merge dictionary with new. Single keys are replaced, but nested dictionaries
        and list are appended
        """
        # we deepcopy new, so that it stays independent from the source
        new = deepcopy(new)
        for key, value in new.items():
            if not dictionary.get(key):
                dictionary[key] = value
            elif isinstance(value, dict):
                cls.update_dict(dictionary[key], value)
            elif isinstance(value, list) and isinstance(dictionary[key], list):
                for item in value:
                    if item not in dictionary[key]:
                        dictionary[key].append(item)
            else:
                dictionary[key] = value

    def _make_cfg_file(self):
        """
        Dump the configuration for a format into a file. This way filter and flight
        scripts can read the configuration.
        """
        # return file_write(CFG_TEMP_FILE, yaml_dump(self.cfg), self.temp_dir)
        return yaml_dump(self.cfg, join(self.temp_dir, CFG_TEMP_FILE))

    def _read_cfg_file(self):
        """Read the cfg file"""
        self.cfg = yaml_load(join(self.temp_dir, CFG_TEMP_FILE))

    def expand_dirs(self, item, key=""):
        return expand_directories(item, key)


def main():
    """Parse the command line arguments and run PandocStyles with the given args"""
    parser = ArgumentParser(description="Runs pandoc with options defined in styles")
    parser.add_argument("files", nargs="*", help="The source files to be converted")
    parser.add_argument(
        "-f",
        "--folder",
        nargs="?",
        const=True,
        help="All files in the folder are converted together.",
    )
    parser.add_argument(
        "-i",
        "--individual",
        action="store_true",
        help="Convert every file given as an individual file .",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=["md", "markdown"],
        metavar="EXT",
        help="If the folder option is used, only convert files "
        "with the given extensions.",
    )
    parser.add_argument(
        "-t",
        "--to",
        nargs="+",
        default=[],
        metavar="FMT",
        help="The formats that should be produced.",
    )
    parser.add_argument(
        "--from-format", metavar="FMT", help="The format of the source files."
    )
    parser.add_argument(
        "--to-file-type",
        metavar="EXT",
        help="The extension of the output file. Only needed in some" "special cases.",
    )
    parser.add_argument(
        "-d", "--destination", metavar="FOLDER", help="The target folder"
    )
    parser.add_argument(
        "-o",
        "--output-name",
        help="The name of the output file without an extension. "
        "Defaults to the name of the first input file.",
    )
    parser.add_argument(
        "-s",
        "--styles",
        nargs="+",
        default=[],
        metavar="STYLE",
        help="Styles to use for the conversion. Replaces styles given " "in the file.",
    )
    parser.add_argument(
        "-a",
        "--add-styles",
        nargs="+",
        default=[],
        metavar="STYLE",
        help="Styles to use for the conversion. Add the styles given "
        "to the styles given in the file.",
    )
    parser.add_argument(
        "--stylepack",
        action="append",
        default=[],
        help="Add a stylepack. Can be invoked multiple times. Format:\n"
        "--stylepack name=style1,style2,...\n"
        "You can ommit specifying styles, then the default style is"
        "used",
    )
    parser.add_argument(
        "--style-file",
        help="Path to the style file that should be used. "
        "Defaults to the style file in the configuration folder.",
    )
    parser.add_argument(
        "-m", "--metadata", help="Path to the metadata file that should be used."
    )
    parser.add_argument(
        "-p",
        "--print",
        action="store_true",
        help="Print the output to stdout. Accepts only one format.",
    )
    parser.add_argument(
        "-w",
        "--working-dir",
        default=getcwd(),
        type=str,
        metavar="FOLDER",
        help="The folder of the source files, for use in macros etc.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Run quiet. Sets logging to ERROR and shows no warnings " "from pandoc.",
    )
    parser.add_argument(
        "--init", action="store_true", help="Create the user configuration folder."
    )
    parser.add_argument(
        "--log",
        default="INFO",
        choices=["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"],
        help="The logging level. " 'Defaults to "INFO"',
    )
    args = parser.parse_args()

    # logging
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=getattr(logging, "ERROR" if args.quiet or args.print else args.log),
    )

    # stylepack unfolding
    args.stylepacks = []
    if args.stylepack:
        for kv in args.stylepack:
            if "=" not in kv:
                args.stylepacks.append(kv)
            else:
                kv = kv.split("=")
                values = make_list(kv[1].split(","))
                args.stylepacks.append({kv[0]: values})

    # initialize config directory
    if args.init:
        if not isdir(CONFIG_DIR):
            copytree(resource_filename(MODULE_NAME, "config_dir"), CONFIG_DIR)
            logging.info(f"Created configuration directory: {CONFIG_DIR}!")
        return

    if args.folder:
        if args.folder is True:
            args.folder = getcwd()
        args.files = [
            f for f in listdir(args.folder) if has_extension(f, args.extensions)
        ]
        args.files.sort()

    if not args.files:
        parser.print_help()
        return

    convert_list = [args.files] if not args.individual else [[f] for f in args.files]

    with change_dir(args.working_dir):
        for files in convert_list:
            ps = PandocStyles(
                files,
                args.to,
                args.from_format,
                args.styles,
                args.add_styles,
                args.metadata,
                args.destination,
                args.output_name,
                args.stylepacks,
                args.style_file,
                args.quiet,
                args.to_file_type,
            )

            if args.print:
                ps.print_output(args.to[0])
            else:
                ps.run()


if __name__ == "__main__":
    main()
