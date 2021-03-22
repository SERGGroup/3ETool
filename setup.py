from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(

    name='EEETool',
    version='0.0.3',
    license='GNU GPLv3',

    author='Pietro Ungar',
    author_email='pietro.ungar@unifi.it',

    description='Tools for performing exergo-economic and exergo-environmental analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://www.dief.unifi.it/vp-473-exergo-economic-analysis-software.html',
    download_url='https://github.com/pietroUngar/3ETool/archive/refs/tags/0.0.2.tar.gz',

    packages=[

        'src', 'src.Tools', 'src.Tools.Other', 'src.Tools.GUIElements', 'src.Tools.CostCorrelations',
        'src.Tools.CostCorrelations.CorrelationClasses', 'src.Tools.EESCodeGenerator', 'src.MainModules',
        'src.BlockSubClasses', 'test'

    ],

    install_requires=[

        'cryptography>=3.4.6',
        'numpy>=1.20.1',
        'pandas>=1.2.3',
        'PyQt5>=5.15.4',
        'setuptools'

    ],

    classifiers=[

        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

      ]

)
