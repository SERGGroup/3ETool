from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(

    name='3ETool',
    version='0.2.5',
    license='GNU GPLv3',

    author='Pietro Ungar',
    author_email='pietro.ungar@unifi.it',

    description='Tools for performing exergo-economic and exergo-environmental analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://tinyurl.com/SERG-3ETool',
    download_url='https://github.com/SERGGroup/3ETool/archive/refs/tags/0.2.5.tar.gz',

    project_urls={

        'Documentation': 'https://firebasestorage.googleapis.com/v0/b/etapp-serggroup.appspot.com/o/3ETool_res%2FOther%2FUser%20Guide-eng.pdf?alt=media&token=db51ff1e-4c63-48b9-8b42-322a2eee44da',
        'Source': 'https://github.com/SERGGroup/3ETool',
        'Tracker': 'https://github.com/SERGGroup/3ETool/issues',

    },

    packages=[

        'EEETools', 'EEETools.Tools', 'EEETools.Tools.Other', 'EEETools.Tools.GUIElements', 'EEETools.Tools.CostCorrelations',
        'EEETools.Tools.CostCorrelations.CorrelationClasses', 'EEETools.Tools.EESCodeGenerator', 'EEETools.MainModules',
        'EEETools.BlockSubClasses', 'test'

    ],

    install_requires=[

        'cryptography>=3.4.6',
        'pyrebase4>=4.4.3',
        'numpy>=1.20.1',
        'pandas>=1.2.3',
        'PyQt5>=5.15.4',
        'setuptools',
        'xlrd',
        'openpyxl',
        'requests',
        'PyGithub',
        'pywin32',
        'pyvis'

    ],

    classifiers=[

        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

      ]

)
