"""Package setup for csvdiff."""

from setuptools import setup, find_packages

setup(
    name="csvdiff",
    version="0.1.0",
    description="CLI tool to semantically diff two CSV files.",
    author="csvdiff contributors",
    python_requires=">=3.10",
    packages=find_packages(exclude=["tests*"]),
    entry_points={
        "console_scripts": [
            "csvdiff=csvdiff.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
