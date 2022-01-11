from EEETools.version import VERSION
from setuptools import setup
from os import path
import platform

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = list()

with open("requirements.txt") as file:

    new_requirements = file.readline().strip("\n").strip("\t").strip()

    while new_requirements:

        if not (not platform.system() == "Windows" and "pywin32" in new_requirements):

            install_requires.append(new_requirements)

        new_requirements = file.readline().strip("\n").strip("\t").strip()

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

    packages=[

        'EEETools', 'EEETools.Tools', 'EEETools.Tools.Other', 'EEETools.Tools.GUIElements', 'EEETools.Tools.CostCorrelations',
        'EEETools.Tools.CostCorrelations.CorrelationClasses', 'EEETools.Tools.EESCodeGenerator', 'EEETools.MainModules',
        'EEETools.BlockSubClasses', 'test'

    ],

    install_requires=install_requires,

    classifiers=[

        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

      ]

)
