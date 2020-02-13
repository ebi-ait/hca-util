import pathlib
from setuptools import setup

# directory containing this file
HERE = pathlib.Path(__file__).parent

# text of the README file
README = (HERE / "README.md").read_text()

# install requirements
INSTALL_REQS = [line.rstrip() for line in open(os.path.join(os.path.dirname(__file__), "requirements.txt"))]

# This call to setup() does all the work
setup(
    name="hca-util",
    version="0.0.1",
    description="This tool is intended to allow HCA wranglers and contributors to upload and download data to/from "
                "the HCA S3 bucket.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ebi-ait/hca_util",
    author="hca-ingest-dev",
    author_email="prabhat@ebi.ac.uk",
    license="Apache License",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Opera  ting System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    platforms=['MacOS X', 'Posix'],
    packages=["hca.util"],
    include_package_data=True,
    install_requires=INSTALL_REQS,
    entry_points={
        "console_scripts": [
            "hca-util=hca.util.hca_cmd:__main__",
        ]
    },
)
