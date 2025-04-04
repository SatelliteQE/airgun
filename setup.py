#!/usr/bin/env python
from setuptools import find_packages, setup

with open('README.rst') as f:
    README = f.read()

setup(
    name='airgun',
    version='0.0.1',  # Should be identical to the version in docs/conf.py!
    description=(
        'A library which is build over Widgetastic and navmazing to make '
        'Satellite 6 UI testing easier.'
    ),
    long_description=README,
    author='RedHat QE Team',
    url='https://github.com/SatelliteQE/airgun',
    install_requires=[
        'cached_property',
        'fauxfactory',
        'navmazing',
        'python-box',
        'pytest',
        'wait_for',
        'webdriver-kaifuku',
        'selenium==4.21.0',
        'widgetastic.core',
        'widgetastic.patternfly',
        'widgetastic.patternfly4',
        'widgetastic.patternfly5',
    ],
    packages=find_packages(exclude=['tests*']),
    package_data={'': ['LICENSE']},
    include_package_data=True,
    license='GNU GPL v3.0',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: LinuxProgramming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
)
