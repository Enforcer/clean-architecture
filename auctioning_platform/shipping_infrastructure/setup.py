from setuptools import find_packages, setup

setup(
    name="shipping_infrastructure",
    version="0.0.0",
    packages=find_packages(),
    install_requires=["injector", "sqlalchemy", "shipping", "db_infrastructure"],
    extras_require={"dev": ["pytest"]},
)
