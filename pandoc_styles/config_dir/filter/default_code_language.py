from pandoc_styles import run_pandoc_styles_filter, CodeBlock, Code


def default_lang(self):
    if not self.classes:
        lang = self.get_metadata("default-code-language")
        if lang:
            self.classes.append(lang)


if __name__ == "__main__":
    # run_pandoc_styles_filter(default_lang, CodeBlock)
    run_pandoc_styles_filter(default_lang, [Code, CodeBlock])
