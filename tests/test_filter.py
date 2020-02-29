import pytest
from pandoc_styles.utils import file_read, file_write, get_file_name
from fixtures import run_script, copy_from_config  # pylint: disable=W0611
# pylint: disable=W0621, W0613, W1401


@pytest.fixture
def test_filter(tmpdir, run_script, copy_from_config):
    def _test_filter(filt, args, fmts, base=TF_BASE):
        copy_from_config(f"filter/{filt}")
        test_base = base.format(filt, f"{{{args}}}")
        test_file = file_write("test.md", test_base, tmpdir)

        for fmt, fmt_txt, fmt_open, fmt_close in fmts:
            target = fmt_txt.format(fmt_open, fmt_close)
            ps = run_script(f'{test_file} -t {fmt}')
            assert ps
            assert ps.stdout == f"INFO: Build {get_file_name(test_file)}.{fmt}\n"
            print(target)
            print("-----------------------------------")
            print(file_read(f"test.{fmt}", tmpdir))
            assert file_read(f"test.{fmt}", tmpdir) == target
    return _test_filter


def test_alignment(test_filter):
    test_filter('alignment.py', '.align_center',
                [('html', TF_HTML_BASE, '<div class="align_center">', '</div>'),
                 ('latex', DIV_LATEX_BASE, '\\begin{center}\n', '\n\n\\end{center}')])


def test_include(tmpdir, test_filter):
    incl_file = file_write("test_incl.md", "Text to Include", tmpdir)
    base = BASE.format("{}", f'~~~{{}}\n{incl_file}\n~~~')
    test_filter('include.py', '.include',
                [('html', HTML_BASE, '<p>Text to Include</p>', ''),
                 ('latex', LATEX_BASE, 'Text to Include', '')],
                base)


def test_new_page(test_filter):
    # base = BASE.format("{}", '~~~{}\n\n~~~')
    test_filter('new_page.py', '.new_page',
                [('html', HTML_BASE, '<div class="pagebreak"></div>', ''),
                 ('latex', LATEX_BASE, r"\clearpage", '')])
    test_filter('new_page.py', '.new_page .odd-page',
                [('latex', LATEX_BASE, r"\cleardoublepage", '')])


def test_noindent(test_filter):
    test_filter('noindent.py', '.noindent',
                [('html', TF_HTML_BASE, '<div class="noindent">', '</div>'),
                 ('latex', DIV_LATEX_BASE, '\\noindent\n', '')])


BASE = """\
---
style-definition:
  all:
    filter: {}
  latex:
    wrap: none
---

The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.

{}

The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.
"""


TF_BASE = BASE.format("{}", """\
::: {}
The campaign brought honours and promotion to many, but
for me it had nothing but misfortune and disaster. I was removed from my
brigade and attached to the Berkshires, with whom I served at the fatal battle
of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which
shattered the bone and grazed the subclavian artery. I should have
fallen into the hands of the murderous Ghazis had it not been for the
devotion and courage shown by Murray, my orderly, who threw me across a
pack-horse, and succeeded in bringing me safely to the British lines.
:::
""")

TF_BASE_CB = BASE.format("{}", """\
~~~{}
The campaign brought honours and promotion to many, but
for me it had nothing but misfortune and disaster. I was removed from my
brigade and attached to the Berkshires, with whom I served at the fatal battle
of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which
shattered the bone and grazed the subclavian artery. I should have
fallen into the hands of the murderous Ghazis had it not been for the
devotion and courage shown by Murray, my orderly, who threw me across a
pack-horse, and succeeded in bringing me safely to the British lines.
~~~
""")

HTML_BASE = """\
<p>The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.</p>
<p>There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.</p>
{}{}
<p>The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.</p>
<p>There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.</p>
"""

TF_HTML_BASE = HTML_BASE.format("", """\
{}
<p>The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.</p>
<p>There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.</p>
{}""")

LATEX_BASE = """\
The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.

{}{}

The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.
"""

TF_LATEX_BASE = LATEX_BASE.format("", """\
{}The campaign brought honours and promotion to many, but for me it had
nothing but misfortune and disaster. I was removed from my brigade and
attached to the Berkshires, with whom I served at the fatal battle of
Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered
the bone and grazed the subclavian artery. I should have fallen into the
hands of the murderous Ghazis had it not been for the devotion and
courage shown by Murray, my orderly, who threw me across a pack-horse,
and succeeded in bringing me safely to the British lines.{}""")

DIV_BASE = BASE.format("{}", """\
:::{}
The campaign brought honours and promotion to many, but for me it had
nothing but misfortune and disaster. I was removed from my brigade and
attached to the Berkshires, with whom I served at the fatal battle of
Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered
the bone and grazed the subclavian artery. I should have fallen into the
hands of the murderous Ghazis had it not been for the devotion and
courage shown by Murray, my orderly, who threw me across a pack-horse,
and succeeded in bringing me safely to the British lines.
:::
""")

DIV_LATEX_BASE = LATEX_BASE.format("", """\
{}
The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.{}\
""")
