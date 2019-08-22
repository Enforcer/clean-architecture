from setuptools import find_packages, setup

setup(
    name="main",
    version="0.0.0",
    packages=find_packages(),
    install_requires=[
        "rq",
        "redis",
        "python-dotenv",
        "injector",
        "sqlalchemy",
        "auctions",
        "auctions_infrastructure",
        "customer_relationship",
        "db_infrastructure",
        "foundation",
        "payments",
        "processes",
        "web_app_models",
    ],
)
