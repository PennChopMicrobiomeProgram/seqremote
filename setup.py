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
        'seqremote_upload = seqremote.main:upload_file',
        'seqremote_check_upload = seqremote.main:check_upload',
        'seqremote_convert = seqremote.main:convert_json',
        ]},
    install_requires=["onecodex", "requests"],
    )
