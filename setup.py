from setuptools import setup, find_packages
from pathlib import Path

README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

setup(
    name="srf-carboncapture",
    version="0.1.0",
    description="Tools for SRF carbon capture workflows",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Your Name",
    url="https://github.com/your-org/srf-carboncapture",
    license="MIT",
    package_dir={"": "src"},                   # <--- tell setuptools where packages live
    packages=find_packages(where="src"),       # <--- find packages under /src
    python_requires=">=3.9",
    install_requires=[],
    include_package_data=True,
)
