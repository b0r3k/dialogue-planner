#!/usr/bin/env python3

from setuptools import setup
from setuptools import find_packages

setup(
    name='dialmonkey',
    version='0.0.1dev',
    description='Dialogue systems framework',
    author='ÚFAL Dialogue Systems Group, Charles University',
    author_email='odusek@ufal.mff.cuni.cz',
    url='https://gitlab.com/ufal/dsg/dialmonkey',
    download_url='https://gitlab.com/ufal/dsg/dialmonkey.git',
    license='Apache 2.0',
    include_package_data=True,
    install_requires=['pyyaml',
                      'cloudpickle',
                      'sklearn',
                      'unidecode',
                      'regex',
                      'tqdm',
                      'logzero'],
    packages=find_packages()
)

