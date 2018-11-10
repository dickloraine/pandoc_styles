from pandoc_styles import run_transform_filter


def latex(self):
    style_pdf = self.classes[1] if len(self.classes) == 2 else self.attributes.get("pdf", "")
    return (f'\\begin{{{style_pdf}}}\n'
            f'{self.convert_text()}\n'
            f'\\end{{{style_pdf}}}\n')


def html(self):
    style_epub = self.classes[1] if len(self.classes) == 2 else self.attributes.get("epub", "")
    return (f'<div class="{style_epub}">\n'
            f'{self.convert_text()}\n'
            f'</div>')


if __name__ == "__main__":
    run_transform_filter(["custom"], latex, html, '{text}')
