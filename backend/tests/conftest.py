import warnings
import pytest


def pytest_configure(config):
    """Suppress known harmless warnings during the test run."""
    warnings.filterwarnings(
        "ignore",
        message="Using the in-memory storage for tracking rate limits",
        category=UserWarning,
    )
