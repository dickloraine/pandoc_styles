# Introduction

This script allows you to define styles for pandoc. In styles you can define, with which arguments pandoc should be invoked for different formats. In addition it allows to run scripts before and after a conversion and gives much power to these scripts and to filters.

# Installation

## Requirements

To use this script, you need the following:

1. Python 3.6 or higher:
    You can get [python here](https://www.python.org/).

2. Pandoc:
    You can download [pandoc here](http://pandoc.org/index.html).

## Install

Now you need to install this script itself. Open the console and enter:

    pip3 install panovel

## Setup

Depending on your system, you may have to configure some settings for everything to work.
Upon installation this script created the directory "pandoc_styles" in your user folder. Inside you can find the config.yaml file. Set the option in there that are needed for your system.

# Usage

The "pandoc_styles" folder can be used as a central point to store styles, scripts, filter etc. Some subfolders are pre-created for you to use.

The "styles.yaml" file contains all the styles. Here you define your styles and the script looks here for styles specified in the metadata block of your files.

To use your styles, your source files need to have a metadata block. Three commands in the block are recognized by this script:

- styles: A list of styles to be used for the file
- style-defintion: In addition of defining styles in the "styles.yaml" file, you can define a style here too. Style settings given here have precedence over those given in "styles.yaml"
- formats: A list of formats the source file should be converted to.

Then to convert your file, open the console and enter:
    pandoc_styles "your_file"

The commandline script has many optional parameters to be useful in macros, batch files etc. Enter
    pandoc_styles -h
to see all the options.

# Defining Styles

## Basic Usage

Styles are written in yaml, just like pandoc metadata-blocks. A style is defined like this:

~~~yaml
Name:
  format:
    command-line:
      pandoc-option: value
    metadata:
      pandoc-variable: value
~~~

"Name" is how the style is adressed. A style directly defined in the metadata-block has no name. "Format" specifies for which format the following commands should be invoked. There is a special value: "all". Everything under "all" is used in any format. Under "command-line" you use the long version of pandoc parameters followed by the value, to invoke them. If a parameter is a flag, use "true". Parameters given the value "false" are ignored. Under "metadata" you enter the names and values of pandoc variables, this are most commonly used in templates.

### A Basic example

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
    command-line:
      toc: true
      toc-depth: 3
      highlight-style: tango
      metadata:
      language: en
  html:
    command-line:
      standalone: true
  pdf:
    command-line:
      pdf-engine: xelatex
---
~~~

## Inheritance

A style can have a field named "inherit". This is a list of other styles it inherits from. Styles lower on the list update styles that are higher. The following rules are in place:

- Single values are replaced
- If a value is another dictionary, new values are appended to it, if a value exists, these rules are used again on it
- If a value is a list, new values are appended to it.

## Advanced Feature
