import pytest
from pandoc_styles.utils import file_read, file_write
from fixtures import run_script, config_dir  # pylint: disable=W0611
# pylint: disable=W0621, W0613, W1401


@pytest.fixture
def test_transform_filter(tmpdir, run_script):
    def _test_filter(filt, args, fmts):
        test_base = BASE.format(f"./config_dir/filter/{filt}", f"{{{args}}}")
        test_file = file_write("test.md", test_base, tmpdir)

        for fmt, fmt_txt, fmt_open, fmt_close in fmts:
            target = fmt_txt.format(fmt_open, fmt_close)
            ps = run_script(f'{test_file} -t {fmt}')
            assert ps.returncode == 0
            assert ps.stdout == f"INFO: Build {fmt}\n"
            assert file_read(f"test.{fmt}", tmpdir) == target
    return _test_filter


def test_alignment(config_dir, test_transform_filter):
    test_transform_filter('alignment.py', '.align .center', [
        ('html', HTML_BASE, '<div class="align_center">', '</div>'),
        ('latex', LATEX_BASE, '\\begin{center}\n', '\n\end{center}')
    ])


def test_epigraph(config_dir, test_transform_filter):
    test_transform_filter('epigraph.py', '.epigraph', [
        ('html', HTML_BASE,
         '<div class="Epigraph">',
         '</div>'),
        ('latex', LATEX_BASE, '\\dictum[]{',
         '}\n\\par\n\\vspace{\\baselineskip}\n\\par\n\\noindent')
    ])
    test_transform_filter('epigraph.py', '.epigraph author="Sherlock Holmes"', [
        ('html', HTML_BASE,
         '<div class="Epigraph">',
         '<p class="EpigraphAuthor">Sherlock Holmes</p>\n</div>'),
        ('latex', LATEX_BASE, '\\dictum[Sherlock Holmes]{',
         '}\n\\par\n\\vspace{\\baselineskip}\n\\par\n\\noindent')
    ])


def test_noindent(config_dir, test_transform_filter):
    test_transform_filter('noindent.py', '.noindent', [
        ('html', HTML_BASE, '<div class="noindent">', '</div>'),
        ('latex', LATEX_BASE, '\\noindent\n', '')
    ])


BASE = """\
---
style-definition:
  all:
    command-line:
      filter: {}
  latex:
    command-line:
      wrap: none
---

The campaign brought honours and promotion to many, but
for me it had nothing but misfortune and disaster. I was removed from my
brigade and attached to the Berkshires, with whom I served at the fatal battle
of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which
shattered the bone and grazed the subclavian artery. I should have
fallen into the hands of the murderous Ghazis had it not been for the
devotion and courage shown by Murray, my orderly, who threw me across a
pack-horse, and succeeded in bringing me safely to the British lines.

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

The campaign brought honours and promotion to many, but
for me it had nothing but misfortune and disaster. I was removed from my
brigade and attached to the Berkshires, with whom I served at the fatal battle
of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which
shattered the bone and grazed the subclavian artery. I should have
fallen into the hands of the murderous Ghazis had it not been for the
devotion and courage shown by Murray, my orderly, who threw me across a
pack-horse, and succeeded in bringing me safely to the British lines.

"""

HTML_BASE = """\
<p>The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.</p>
<p>There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.</p>
{}
<p>The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.</p>
<p>There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.</p>
{}
<p>The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.</p>
<p>There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.</p>
"""

LATEX_BASE = """\
The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.

{}The campaign brought honours and promotion to many, but for me it had
nothing but misfortune and disaster. I was removed from my brigade and
attached to the Berkshires, with whom I served at the fatal battle of
Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered
the bone and grazed the subclavian artery. I should have fallen into the
hands of the murderous Ghazis had it not been for the devotion and
courage shown by Murray, my orderly, who threw me across a pack-horse,
and succeeded in bringing me safely to the British lines.{}

The campaign brought honours and promotion to many, but for me it had nothing but misfortune and disaster. I was removed from my brigade and attached to the Berkshires, with whom I served at the fatal battle of Maiwand.

There I was struck on the shoulder by a Jezail bullet, which shattered the bone and grazed the subclavian artery. I should have fallen into the hands of the murderous Ghazis had it not been for the devotion and courage shown by Murray, my orderly, who threw me across a pack-horse, and succeeded in bringing me safely to the British lines.
"""
