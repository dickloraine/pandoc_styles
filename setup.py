from os import path
from shutil import copytree
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from pkg_resources import resource_filename


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def init_user_config():
    base_dir = path.join(path.expanduser("~"), "pandoc_styles")
    if path.isdir(base_dir):
        return
    copytree(resource_filename('pandoc_styles', 'config_dir'), base_dir)

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        init_user_config()
        develop.run(self)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        init_user_config()
        install.run(self)


setup(
    name='pandoc_styles',
    version='0.2',
    description='A script to convert files with pandoc using styles',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='dickloraine',
    author_email='dickloraine@gmx.net',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Text Processing',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='pandoc writing text conversion',

    packages=['pandoc_styles'],
    python_requires='>=3.6',
    package_data={
        'pandoc_styles': ['*.md', '*.yaml', 'config_dir/*.*'],
    },
    install_requires=[
        'pyYaml',
        'panflute',
        'libsass',
    ],
    entry_points={
        'console_scripts': ['pandoc_styles=pandoc_styles.main:main'],
    },
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    zip_safe=False
)
