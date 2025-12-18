from setuptools import setup, find_packages

setup(
    name="moie_os_core",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0",
        "numpy>=1.24.0",
        "rich>=13.0.0",
        "typer>=0.9.0",
    ],
)
