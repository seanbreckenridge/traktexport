from pathlib import Path
from setuptools import setup, find_packages

long_description = Path("README.md").read_text()
reqs = Path("requirements.txt").read_text().strip().splitlines()

pkg = "traktexport"
setup(
    name=pkg,
    version="0.1.4",
    url="https://github.com/seanbreckenridge/traktexport",
    author="Sean Breckenridge",
    author_email="seanbrecke@gmail.com",
    description=("""Export your Movies, TV shows and ratings"""),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(include=[pkg]),
    install_requires=reqs,
    python_requires=">=3.7",
    package_data={pkg: ["py.typed"]},
    keywords="media movies export data",
    entry_points={"console_scripts": ["traktexport = traktexport.__main__:main"]},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
