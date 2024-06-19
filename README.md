# pandoc-styles

This script allows you to define styles for pandoc. In styles you can define, with which arguments pandoc should be invoked for different formats. In addition it allows to run scripts before and after a conversion and gives much power to these scripts and to filters.

- [pandoc-styles](#pandoc-styles)
  - [Installation](#installation)
    - [Requirements](#requirements)
    - [Install](#install)
      - [Via pipx](#via-pipx)
      - [Local python](#local-python)
    - [Setup](#setup)
  - [Usage](#usage)
  - [Defining Styles](#defining-styles)
    - [Basic Usage](#basic-usage)
    - [Inheritance](#inheritance)
  - [Stylepacks](#stylepacks)
  - [Advanced Feature](#advanced-feature)
    - [Adressing files in the configuration folder](#adressing-files-in-the-configuration-folder)
    - [Verbatim Variables](#verbatim-variables)
    - [Preflight](#preflight)
    - [Process Sass](#process-sass)
    - [Add to template](#add-to-template)
    - [Replace in template](#replace-in-template)
    - [Replace in output](#replace-in-output)
    - [Postflight](#postflight)
    - [Filter](#filter)
    - [Advanced Example](#advanced-example)
  - [Commandline tools](#commandline-tools)
  - [Creating stylepacks](#creating-stylepacks)

## Installation

### Requirements

To use this script, you need the following:

1. Python 3.6 or higher:
    You can get [python here](https://www.python.org/).

2. Pandoc 3.1 or higher:
    You can download [pandoc here](http://pandoc.org/index.html).

3. (Optional) pipx:
    You can find [installation instruction here](https://pipx.pypa.io/stable/installation/)

### Install

Now you need to install this script itself.

#### Via pipx

The recommended way is via [pipx](https://pipx.pypa.io/stable/). This runs the script in an isolated environment.

Open the console and enter:

    pipx install pandoc-styles
    pandoc-styles --init

If you need additional python packages in the isolated environment, you can install them via

    pipx inject pandoc-styles package-name

If you for example need the matplotlib stack use

    pipx inject pandoc-styles numpy scipy matplotlib pandas sympy nose

#### Local python

You can install the script into your local python environment

Open the console and enter:

    pip3 install pandoc_styles
    pandoc-styles --init

### Setup

Depending on your system, you may have to configure some settings for everything to work.
Upon initialization this script created the directory "pandoc_styles" in your user folder. Inside you can find the config.yaml file. Set the option in there that are needed for your system.

## Usage

The "pandoc_styles" folder can be used as a central point to store styles, scripts, filter etc. Some subfolders are pre-created for you to use.

The "styles.yaml" file contains all the styles. Here you define your styles and the script looks here for styles specified in the metadata block of your files.

To use your styles, your source files need to have a metadata block. These commands in the block are recognized by this script:

- styles: A list of styles to be used for the file
- style-defintion: In addition of defining styles in the "styles.yaml" file, you can define a style here too. Style settings given here have precedence over those given in "styles.yaml"
- formats: A list of formats the source file should be converted to. If none is given, html- and pdf-files are build.
- destination: A directory to create the output in.
- output-name: The desired name of the outputfile without extension. In none is given, the filename is used.
- fields that exist in the style. They override the default given in the style.

If you convert all files in a folder as one document, these additional commands are available:

- file-list: Specify exactly which files in the folder should be converted.
- excluded-files: Exclude the listed files from beeing converted.

Then to convert your file, open the console and enter:

    pandoc-styles "your_file"

Or if you want to convert all files in a folder as one document:
    pandoc-styles -f

The commandline script has many optional parameters to be useful in macros, batch files etc. Enter

    pandoc-styles -h

to see all the options.

## Defining Styles

### Basic Usage

Styles are written in yaml, just like pandoc metadata-blocks. A style is defined like this:

~~~yaml
Name:
  format:
      pandoc-option: value
      pandoc-variable: value
~~~

"Name" is how the style is adressed. A style directly defined in the metadata-block has no name. "Format" specifies for which format the following commands should be invoked. There is a special value: "all". Everything under "all" is used in any format. Examples for formats are html, pdf, latex, epub etc.

Under the format you just enter pandoc options and variables. If a parameter is a flag, use "true". Parameters given the value "false" are ignored.

**A Basic example**

This is an example metadata-block in a source file:

~~~yaml

---
title:  Example
author: John Doe
formats:
    - html
    - pdf
style-definition:
    all:
        toc: true
        toc-depth: 3
        highlight-style: tango
        language: en
    html:
        standalone: true
    pdf:
        pdf-engine: xelatex
---
~~~

### Inheritance

A style can have a field named "inherit". This is a list of other styles it inherits from. Styles lower on the list update styles that are higher. The following rules are in place:

- Single values are replaced
- If a value is another dictionary, new values are appended to it, if a value exists, these rules are used again on it
- If a value is a list, new values are appended to it.

## Stylepacks

It is possible, to bundle all files necessary for a particular style and share this as a stylepack. You can install a stylepack either through extracting its contents into the styles folder inside the config folder or through the pandoc_styles_tools command line interface with the option `import` command.

To use a stylepack, include a field "stylepacks" in the matadata. It looks like this:

~~~
stylepacks:
  - stylepack_1_name:
    - style_1
    - style2
  - stylepack_2_name
~~~

If you do not specify styles from the stylepack, it uses its default style.

**Example**

[pandoc_styles: novel](https://github.com/dickloraine/pandoc_styles_novel) is a stylepack to create novels out of your source files. A documentation for using this stylepack is found on the github page and inside the style folder of the pack once installed. You can install it with this command:

~~~
pandoc-styles-tools import novel -u https://github.com/dickloraine/pandoc_styles_novel/releases/latest/download/novel.zip
~~~

## Advanced Feature

### Adressing files in the configuration folder

You can point to a file in the configuration directory, if you prepend the path with "~/". The script searches first for the given path and then looks in appropiatly named subfolders and finally in the "misc" subfolder. For example:

~~~yaml
filter:
  - ~/test-filter.py
~~~

Would find the file "test-filter.py" in the subfolder "filter" in the configuration directory.

### Verbatim Variables

If you need template variables that should not be rendered in the output format (for example file paths), you can add these under the "verbatim-variables" field:

~~~yaml
verbatim-variables:
  my-path: "my/path"
~~~

Some variables are predefiened and always usable in templates:

- config-dir: The path to the config dir
- stylepackName-dir: The path to the directory of the given stylepack
- temp-dir: The path to the currently used temporary directory

### Preflight

You can run other command-line apps and scripts before the conversion happens. Just enter the command-line command in the preflight field in the style definition. You can pass the files list to it with `<files>`. Explicitly mark the value as a string, to avoid any hassle with special characters. For example:

~~~yaml
Test-style:
  html:
    preflight:
      - 'some_app -d -f <files>'
~~~

If you give it just a single python file, it assumes that it is a special preflight script. These are written in python and have access to the style infos and files that should be converted.

Here a basic example of a preflight script, that appends text given in the field "append-to-file" in the style definition to the end of the files:

~~~python
from pandoc_styles import run_preflight_script, file_read, file_write


def preflight(self):
    text_to_append = self.cfg["append-to-file"]
    if isinstance(text_to_append, list):
        text_to_append = "\n".join(text_to_append)
    file_write(self.files[-1], f"{file_read(self.files[-1])}\n{text_to_append}")


if __name__ == '__main__':
    run_preflight_script(preflight)
~~~

Modify only the preflight function to include your code.

And to run it in your style definition:

~~~yaml
Test-style:
  html:
    preflight:
      - append-to-file.py
    append-to-file: "Test"
~~~

### Process Sass

You can point to sass-files that should be used for html output and this script converts them for you to css and uses that in the output. In addition you can define variables used in the sass file and specify, where the compiled css file shoud be copied.

~~~yaml
Test-style:
  html:
    sass:
      files: ~/default.scss
      output-path: temp
      variables:
        body-font-size: 10pt
~~~

"files" is a list of sass files to be included.

"output-path" can be "~/" to output to the css folder in the configuration folder, a relative path or "temp" to be used with the "self-contained" parameter. If ommited, the css output is in the same folder as the source files output.

"variables" can be any variables in your sass files.

### Add to template

Sometimes you want to include some code directly into the template, instead of just including it in the header. Mostly, if you want to define and use your own template variables.

This option just injects the given code directly into the head of the template.

It accepts a path to a file and will add the contents of the file to the template.

~~~yaml
Test-style:
  pdf:
    add-to-template:
      - |
        \titlehead{{$titletop-left$
        \hfill $titletop-right$\\}
        $titlehead$}
        \publishers{\small $titlebottom$}
~~~

### Replace in template

As above, but instead of just adding the code to the head, it replaces arbitrary text in the template. You need to give it a pattern and a replacement text. Optionally you can use the flag "add" to not replace the text, but prepend to it and the field "count" if only some matches should be replaced.

~~~yaml
Test-style:
  html:
    replace-in-template:
      - pattern: \$body\$
        replacement-text: |
          <div class="content">
          $body$
          </div>
~~~

### Replace in output

Exactly the same as replace-in-template but for text in the output-file

### Postflight

These scripts are called after the source is converted. Pretty similar to preflight, but instead of `<files>` it only accepts a single `<file>`

**Some app:**

~~~yaml
Test-style:
  html:
    preflight:
      - 'some_app -d -f <file>'
~~~

**Custome script:**

~~~python
from pandoc_styles import run_postflight_script, file_read, file_write


def postflight(self):
    text_to_append = self.cfg["append-to-output"]
    if isinstance(text_to_append, list):
        text_to_append = "\n".join(text_to_append)
    file_write(ffile, f"{file_read(ffile)}\n{text_to_append}")


if __name__ == '__main__':
    run_postflight_script(postflight)
~~~

~~~yaml
Test-style:
  html:
    preflight:
      - append-to-output.py
    append-to-output: "Test"
~~~

### Filter

This script includes some functionality to make writing filters a little bit more easy.

### Advanced Example

Pandocs self-contained flag doesn't work for html if math is used, because mathjax can't be included. This style is not really self-contained, but it allows for single files with all css included. This example useses the default.sass file included in this script. Fonts are also just referenced instead of included, to make for small file-sizes.

For code in pdfs, it introduces line-wrap in code blocks and ligatures in the font.

In addition, inheritance is shown.

~~~yaml
All:
  all:
    lang: en
  pdf:
    pdf-engine: "xelatex"

Math-document:
  inherits:
    - Code
  html:
    self-contained: true
    mathjax: true
    sass:
      files: ~/default.scss
      output-path: temp
    replace-in-template:
      - pattern: \$body\$
        replacement-text: |
          <div class="content">
          $body$
          </div>
      - pattern: \$table-of-contents\$
        replacement-text: |
          <div id="sidebar">
          <input class="trigger" type="checkbox" id="mainNavButton">
          <label for="mainNavButton" onclick></label>
          $table-of-contents$
          </div>
    replace-in-output:
      - pattern: (<\/head>)
        count: 1
        add: true
        replacement-text: |
          <link href="https://fonts.googleapis.com/css?family=Noto+Sans|Noto+Serif|Oswald" rel="stylesheet">
          <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/tonsky/FiraCode@1.206/distr/fira_code.css">
      - pattern: <script type="text\/javascript">\/\*\n\s+\*\s+\/MathJax\.js.*?<\/script>
        replacement-text: |
          <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.2/MathJax.js?config=TeX-AMS_CHTML-full" type="text/javascript"></script>

Code:
  all:
    highlight-style: tango
  pdf:
    monofont: Fira Code
    # allow code line break
    add-to-template:
      - |
        \usepackage{fvextra}
        \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakautoindent=true,commandchars=\\\{\}}
      - |
        \setmonofont[
          Contextuals={Alternate}
        ]{$monofont$}
        \makeatletter
        \def\verbatim@nolig@list{}
        \makeatother
~~~

## Commandline tools

Some additional tools are available on the commandline with the command:

```bash
pandoc-styles-tools
```

The import option is used to import stylepacks.

One tool merges styles and outputs the new style in a file.

The localize tool copies all used assets into the local directory, to have a self-contingent project folder.

## Creating stylepacks

To create a stylepack, just create a folder with the name of the stylepack. Inside the folder put a yaml file containing the style definitions with the name of the stylepack. Then mimick the config folder for organizing the files provided.

In the yaml file reference links to files inside the stylepack with "stylepack_name@path".

Create a zip of your folder (with the folder inside the zip) and name it after your stylepack.
