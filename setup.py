from EEETools.version import VERSION
from setuptools import setup
from os import path, listdir

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def __get_install_requires():

    install_requires = [

        'future~=0.18.2',
        'PyQt5~=5.15.4',
        'pandas~=1.2.3',
        'openpyxl~=3.0.7',
        'cryptography~=3.4.6',
        'pyvis~=0.1.9',
        'rply~=0.7.8',
        'setuptools~=54.2.0',
        'xlrd~=1.2.0',
        'numpy'

    ]

    import platform

    if platform.system() == "Windows":
        install_requires.append('pywin32')

    return install_requires


def __get_packages() -> list:

    ROOT_DIR = path.join(path.dirname(__file__), "EEETools")
    TEST_DIR = path.join(path.dirname(__file__), "test")
    packages = append_sub_dir(ROOT_DIR, list())
    packages = append_sub_dir(TEST_DIR, packages)
    return packages


def append_sub_dir(element_path, input_list: list, parent_name=None) -> list:

    if path.isdir(element_path):

        name = path.basename(element_path)

        if "__" not in name:

            if parent_name is not None:
                name = "{}.{}".format(parent_name, name)

            input_list.append(name)

            for sub_name in listdir(element_path):
                input_list = append_sub_dir(path.join(element_path, sub_name), input_list, parent_name=name)

    return input_list


setup(

    name='3ETool',
    version=VERSION,
    license='GNU GPLv3',

    author='Pietro Ungar',
    author_email='pietro.ungar@unifi.it',

    description='Tools for performing exergo-economic and exergo-environmental analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://tinyurl.com/SERG-3ETool',
    download_url='https://github.com/SERGGroup/3ETool/archive/refs/tags/{}.tar.gz'.format(VERSION),

    project_urls={

        'Documentation': 'https://drive.google.com/file/d/1Dzdz4_EAKyY9c8nOm2SKTIqSXfV74w2-/view?usp=sharing',
        'Source': 'https://github.com/SERGGroup/3ETool',
        'Tracker': 'https://github.com/SERGGroup/3ETool/issues',

    },

    packages=__get_packages(),

    install_requires=__get_install_requires(),

    classifiers=[

        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

    ]

)
