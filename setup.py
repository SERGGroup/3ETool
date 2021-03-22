from setuptools import setup

setup(

    name='3ETool',
    version='0.0.1',
    packages=['src', 'src.Tools', 'src.Tools.Other', 'src.Tools.GUIElements', 'src.Tools.CostCorrelations',
              'src.Tools.CostCorrelations.CorrelationClasses', 'src.Tools.EESCodeGenerator', 'src.MainModules',
              'src.BlockSubClasses', 'test'],
    url='https://www.dief.unifi.it/vp-473-exergo-economic-analysis-software.html',
    license='',
    author='Pietro Ungar',
    author_email='pietro.ungar@unifi.it',
    description='Tools for performing exergo-economic and exergo-environmental analysis',
    install_requires = [

        'cryptography>=3.4.6',
        'numpy>=1.20.1',
        'PyQt5>=5.15.4',
        'pandas>=1.2.3',
        'setuptools'

    ]

)
