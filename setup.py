#!/usr/bin/env python

from distutils.core import setup

setup(
    name='seqremote',
    version="0.0.1",
    description='Process sequence data remotely',
    author='Kyle Bittinger',
    author_email='kylebittinger@gmail.com',
    url='https://github.com/PennChopMicrobiomeProgram',
    packages=['seqremote'],
    entry_points={'console_scripts': [
        'seqremote_assign = seqremote.main:assign_file',
        'seqremote_retrieve = seqremote.main:retrieve_analyses',
        ]},
    install_requires=["onecodex", "requests"],
    )
