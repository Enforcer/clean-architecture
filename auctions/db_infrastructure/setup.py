from setuptools import find_packages, setup

setup(
    name="db_infrastructure",
    version="0.0.0",
    packages=find_packages(),
    install_requires=["sqlalchemy", "pytest-sqlalchemy"],
)
