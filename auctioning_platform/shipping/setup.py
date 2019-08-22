from setuptools import find_packages, setup

setup(
    name="shipping",
    version="0.0.0",
    packages=find_packages(),
    install_requires=["injector"],
    extras_require={"dev": ["pytest"]},
)
