from _pytest.config.argparsing import Parser


def pytest_addoption(parser: Parser) -> None:
    """
    Adds a pytest_addoption.

    Args:
        parser: (todo): write your description
    """
    parser.addoption("--stripe-publishable-key", action="store")
    parser.addoption("--stripe-secret-key", action="store")
