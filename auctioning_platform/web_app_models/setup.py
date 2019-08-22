from setuptools import find_packages, setup

setup(
    name="web_app_models",
    version="0.0.0",
    packages=find_packages(),
    install_requires=["Flask-Security", "sqlalchemy", "db_infrastructure"],
    extras_require={"dev": ["pytest"]},
)
