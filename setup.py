#!/usr/bin/env python2

import os
from pip.req import parse_requirements
from setuptools import setup, find_packages

from gogeta_configure import __version__

repo_directory = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(repo_directory,'README.rst')).read()
except:
    long_description = None

setup(
    name='gogeta-configure',
    version=__version__,
    packages=find_packages(exclude=['test*']),

    author='Sam J Sharpe',
    author_email='sam@samsharpe.net',
    maintainer='Sam J Sharpe',
    url='https://github.com/samjsharpe/gogeta-configure',

    description='gogeta-configure: Maintain etcd configuration for gogeta from YAML file',
    long_description=long_description,
    license='MIT',
    keywords='gogeta etcd yaml',

    install_requires=[
        'requests>=2.5.0',
        'PyYAML>=3.1.1'
    ],

    setup_requires=['setuptools-pep8'],

    tests_require=[
        'nose==1.3.3'
    ],

    test_suite='nose.collector',

    entry_points={
        'console_scripts': [
            'gogeta-configure=gogeta_configure.main:main'
        ]
    }

)
