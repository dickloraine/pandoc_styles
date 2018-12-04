from pandoc_styles import run_transform_filter


if __name__ == "__main__":
    run_transform_filter(
        ["noindent", "no-indent", "no_indent"],
        '\\noindent\n{text}\n',
        '<div class="noindent">\n{text}\n</div>')
