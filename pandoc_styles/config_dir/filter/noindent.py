from pandoc_styles import run_transform_filter


if __name__ == "__main__":
    run_transform_filter(
        ["noindent", "no-indent", "no_indent"],
        latex=['\\noindent', 'text'],
        html=['<div class="noindent">', 'text', '</div>'])
