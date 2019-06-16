from setuptools import find_packages, setup

setup(
    name="processes",
    version="0.0.0",
    packages=find_packages(),
    install_requires=["injector", "sqlalchemy", "foundation", "auctions", "db_infrastructure"],
    extras_require={"dev": ["pytest"]},
)
