from pandoc_styles import run_transform_filter


def latex(self):
    if "left" in self.classes:
        style = "flushleft"
    elif "right" in self.classes:
        style = "flushright"
    else:
        style = "center"

    return (f'\\begin{{{style}}}\n'
            f'{self.convert_text()}\n'
            f'\\end{{{style}}}\n')


def html(self):
    if "left" in self.classes:
        style = "left"
    elif "right" in self.classes:
        style = "right"
    else:
        style = "center"

    return (f'<div class="align_{style}">\n'
            f'{self.convert_text()}\n'
            f'</div>')


if __name__ == "__main__":
    run_transform_filter(["align"], latex, html)
