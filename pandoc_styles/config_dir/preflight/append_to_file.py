from pandoc_styles import run_preflight_script, file_read, file_write


def preflight(self):
    text_to_append = self.cfg["append-to-file"]
    if isinstance(text_to_append, list):
        text_to_append = "\n".join(text_to_append)
    file_write(self.files[-1], f"{file_read(self.files[-1])}\n{text_to_append}")


if __name__ == '__main__':
    run_preflight_script(preflight)
