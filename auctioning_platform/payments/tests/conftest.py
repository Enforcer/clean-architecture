from _pytest.config.argparsing import Parser


def pytest_addoption(parser: Parser) -> None:
    parser.addoption("--stripe-publishable-key", action="store")
    parser.addoption("--stripe-secret-key", action="store")
