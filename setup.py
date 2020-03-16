import os
import pathlib
from setuptools import setup

# directory containing this file
HERE = pathlib.Path(__file__).parent

# text of the README file
README = (HERE / 'README.md').read_text()

# install requirements
INSTALL_REQS = [line.rstrip() for line in open(os.path.join(os.path.dirname(__file__), 'requirements.txt'))]

# This call to setup() does all the work
setup(
    # dashes are ok in repo and PyPI dist names but not in package (i.e. directory) and
    # module (.py file) names. can't do import xyz-abc
    name='hca-util',
    version='0.1.2',
    description='CLI tool for file transfer (upload and download) to/from AWS S3.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/ebi-ait/hca-util',
    author='hca-ingest-dev',
    author_email='prabhat@ebi.ac.uk',
    license='Apache License',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    platforms=['MacOS X', 'Posix'],
    packages=['hca_util', 'hca_util.command'],
    include_package_data=True,
    install_requires=INSTALL_REQS,
    entry_points={
        'console_scripts': [
            'hca-util=hca_util.__main__:main',
        ]
    },
)
