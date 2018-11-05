import re
import logging
import yaml
from pandoc_styles import run_preflight_script, file_read, file_write


def make_appendices(self):
    '''
    Make appendices out of data-files and style options that render this data.
    These are given in the metadata with a list called 'appendices'.
    '''
    if not self.cfg.get("appendices"):
        return

    if any(appendix.get('only-linked') for appendix in self.cfg["appendices"].values()):
        # search for links possibly containing a link to an item in the databases
        link_pattern = re.compile(r'\[.*?\]\(#(.*?)\)', re.DOTALL)
        candidates = [x for f in self.files for x in link_pattern.findall(file_read(f))]

    for name, appendix in self.cfg["appendices"].items():
        try:
            data = appendix.get("data-file", self.cfg.get("data-file", {}).get(name, ""))
            data = yaml.load_all(file_read(data))
        except FileNotFoundError:
            logging.error(f'{appendix["data-file"]} not found.')
            continue

        if appendix.get('sort'):
            key = appendix.get('sort', "name")
            data = sorted(data, key=lambda x: x[key])

        classes = appendix.get("classes", f".{name}")
        appendix_heading_level = appendix.get("appendix-heading-level", 1)
        header = ".hidden-heading" if appendix.get('hidden-heading') else "-"
        title = appendix.get("title", name.capitalize())
        entry_heading_level = self.cfg.get("appendix-entry-heading-level",
                                           appendix_heading_level + 1)

        data_text = [f'{"#" * appendix_heading_level} {title}\n']
        for entry in data:
            if (
                    (appendix.get('only-linked') and not
                     entry["name"].lower().replace(' ', '-') in candidates)
                    or
                    (appendix.get('entries') and not
                     entry["name"] in appendix['entries'])
            ):
                continue
            data_text.append(f'{"#" * entry_heading_level} {entry["name"]}'
                             f'{{{header} .appendix}}\n')
            data_text.append(f'~~~{{{classes}}}')
            data_text.append(f'{entry["name"]}\n~~~\n')

        data_text = '\n'.join(data_text)
        file_write(self.files[-1], f"{file_read(self.files[-1])}\n{data_text}")


if __name__ == '__main__':
    run_preflight_script(make_appendices)
