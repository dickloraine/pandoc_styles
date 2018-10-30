from os import path, mkdir
from shutil import copy
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
    mkdir(base_dir)
    copy(resource_filename('pandoc_styles', 'styles.yaml'), base_dir)
    copy(resource_filename('pandoc_styles', 'config.yaml'), base_dir)
    mkdir(path.join(base_dir, "filter"))
    mkdir(path.join(base_dir, "templates"))
    mkdir(path.join(base_dir, "preflight"))
    mkdir(path.join(base_dir, "postflight"))
    mkdir(path.join(base_dir, "css"))
    mkdir(path.join(base_dir, "misc"))

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
    description='A script to make a novel out of markdown files with the help of pandoc',
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
        'pandoc_styles': ['*.md', 'filter/*.*', '*.yaml', 'templates/*.*'],
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
