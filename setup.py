#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="lidlplus-ui",
    version="0.1.2",
    author="Zsombor Kalmar",
    description="Desktop version of the Lidl Plus mobile app using my own implementation of the Lidl Plus api.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "GitHub": "https://github.com/zsobix/lidlplus-ui",
        "PyPI": "https://pypi.org/project/lidlplus-ui/",
    },
    license="GPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.14",
    ],
    platforms="any",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "requests >= 2.33.1",
        "qrcode >= 8.2",
        "pyjwkest >= 1.4.4",
        "PyGObject >= 3.56.2",
        "playwright >= 1.58.0",
        "lidlplus-api >= 0.0.5",
        "pillow >= 12.2.0",
        "distro >= 1.9.0"
    ],
    entry_points={
        "console_scripts": [
            "lidlplus-ui = lidlplus_ui.__main__:lidl_plus_run",
        ]
    },
)
