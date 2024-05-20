from os.path import expanduser, join

# Generel constants
MODULE_NAME = "pandoc_styles"
CONFIG_DIR = join(expanduser("~"), MODULE_NAME)
STYLE_FILE = join(CONFIG_DIR, "styles.yaml")
PANDOC_CMD = "pandoc"
FMT = "fmt"
TO_FMT = "to_fmt"
OUTPUT_FILE = "output_file"
CFG_TEMP_FILE = "cfg.yaml"
ALL_STYLE = "All"
DEFAULT_STYLE = "Default"
USER_DIR_PREFIX = "~/"
PATH_MISC = "misc"
PATH_TEMP = "temp"
PATH_SASS = "sass"
PATH_CSS = "css"
PATH_STYLE = "styles"
MODIFIED_FILES = "modified_files"

# Metadata fields constants
MD_VERBATIM_VARIABLES = "verbatim-variables"
MD_EXPANDABLE_VARIABLES = "expandable-variables"
MD_STYLE_PACKS = "stylepacks"
MD_FILE_LIST = "file-list"
MD_EXCLUDED_FILES = "excluded-files"
MD_DESTINATION = "destination"
MD_OUTPUT_NAME = "output-name"
MD_FORMATS = "formats"
MD_FROM_FORMAT = "from-format"
MD_STYLE_FILE = "style-file"
MD_STYLE = "style"
MD_INHERITS = "inherits"
MD_STYLE_DEF = "style-definition"
MD_CURRENT_FILES = "current-files"
MD_TEMP_DIR = "temp-dir"
MD_CFG_DIR = "config-dir"
MD_PANDOC_STYLES_MD = "pandoc_styles_"
MD_PREFLIGHT = "preflight"
MD_POSTFLIGHT = "postflight"
MD_SASS = "sass"
MD_SASS_OUTPUT_PATH = "output-path"
MD_SASS_NAME = "stylesheet-name"
MD_SASS_FILES = "files"
MD_SASS_VARS = "variables"
MD_SASS_APPEND = "append"
MD_ADD_TO_TEMPLATE = "add-to-template"
MD_REPL_IN_TEMPLATE = "replace-in-template"
MD_REPL_PATTERN = "pattern"
MD_REPL_TEXT = "replacement-text"
MD_REPL_ADD = "add"
MD_REPL_COUNT = "count"
MD_TEMPLATE = "template"
MD_REPL_IN_OUTPUT = "replace-in-output"

# Configuartion constants
CFG_FILE = "config.yaml"
CFG_PANDOC_PATH = "pandoc-path"
CFG_PYTHON_PATH = "python-path"

# Some formats:
ALL_FMTS = "all"
HTML = "html"
PDF = "pdf"
LATEX = "latex"
EPUB = "epub"
CSS = "css"

# Filter
FIL_OTHER = "other"
FIL_ALL = "all_formats"
FIL_CHECK = "check"

# Latex formats
LATEX_FORMATS = [LATEX, PDF, "beamer"]
