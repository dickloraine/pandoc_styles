# This filter puts the classname from a div in the markdown into a latex environment
# You can give the environment a different name with the pdf attribute
# You can disable this by setting the attribute no-pdf to true

from pandoc_styles import run_pandoc_styles_filter, Div, LATEX


def latex(self):
    if self.fmt != LATEX:
        return

    if self.attributes.get("no-pdf", False):
        return []

    style_pdf = self.attributes.get("pdf", "") or self.classes[0]
    return (f'\\begin{{{style_pdf}}}\n'
            f'{self.stringify().strip()}'
            f'\\end{{{style_pdf}}}\n')

if __name__ == "__main__":
    run_pandoc_styles_filter(latex, Div)
