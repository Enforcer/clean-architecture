from setuptools import find_packages, setup

setup(
    name="web_app",
    version="0.0.0",
    packages=find_packages(),
    install_requires=[
        "Flask-Security",
        "Flask-Injector",
        "Flask",
        "bcrypt",
        "marshmallow",
        "Flask-Login",
        "sqlalchemy",
        "web_app_models",
        "db_infrastructure",
        "main",
        "foundation",
        "auctions",
    ],
    extras_require={"dev": ["pytest"]},
)
