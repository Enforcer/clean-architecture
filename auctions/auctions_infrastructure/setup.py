from setuptools import find_packages, setup

setup(
    name="auctions_infrastructure",
    version="0.0.0",
    packages=find_packages(),
    install_requires=["injector", "pytz", "sqlalchemy", "foundation", "auctions", "db_infrastructure"],
    extras_require={"dev": ["pytest"]},
)
