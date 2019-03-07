#!/usr/bin/env python

import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name='cisco_dna_center',
    version='1.2.10.0',
    author='Robert Sayle',
    author_email='rsayle@cisco.com',
    description='A wrapper for using Cisco DNA Center\'s REST API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://developer.cisco.com/codeexchange/github/repo/rsayle/DNAC-Python-Wrapper',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: Cisco Sample Code License',
        'Operating System :: OS Independent'
    ],
    install_requires=[
        'requests',
        'json'
    ]
)
