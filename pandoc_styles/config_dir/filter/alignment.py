from pandoc_styles import run_transform_filter


def latex(self):
    if "align_left" in self.classes:
        style = "flushleft"
    elif "align_right" in self.classes:
        style = "flushright"
    else:
        style = "center"

    return [f'\\begin{{{style}}}',
            self.content,
            f'\\end{{{style}}}']


if __name__ == "__main__":
    run_transform_filter(["align_left", "align_right", "align_center"], latex=latex)
