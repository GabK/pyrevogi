from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='PyRevogi',

    version='0.0.1',

    description='Python driver for Revogi smart bulbs',
    long_description=long_description,

    url='https://github.com/GabK/pyrevogi',

    author='Gabriel Kenderessy',
    author_email='g@brie.lk',

    license='Apache-2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: System :: Hardware :: Hardware Drivers',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='revogi smart lightbulb',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['pybluez[ble]'],
    entry_points={
        'console_scripts': [
            'pyrevogi=pyrevogi:main',
        ],
    },
)