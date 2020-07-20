import os
import pathlib
from setuptools import setup
from ait.commons.util.settings import NAME, VERSION, DESC, AUTHOR, AUTHOR_EMAIL

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
    name=NAME,
    version=VERSION,
    description=DESC,
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/ebi-ait/hca-util',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license='Apache License',
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    platforms=['MacOS X', 'Posix'],
    packages=['ait.commons.util','ait.commons.util.settings', 'ait.commons.util.command'],
    include_package_data=True,
    install_requires=INSTALL_REQS,
    entry_points={
        'console_scripts': [
            f'{NAME}=ait.commons.util.__main__:main',
        ]
    },
)
