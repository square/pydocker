#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Square Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# from setuptools import setup, find_packages
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['docker', 'click', 'delegator.py', 'google-auth']

extras_require = {'test': ['pytest', 'flake8']}

setup(
    name='sq-pydocker',
    version='0.2.3',
    description='Python package to make it easier to manage docker containers',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Damien Ramunno-Johnson',
    author_email='damien@squareup.com',
    entry_points={'console_scripts': ['pydocker = pydocker.cli:cli']},
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    zip_safe=False,
    keywords='pydocker',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
