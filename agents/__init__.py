"""Automation package for Eternia agents."""

from importlib import metadata

__all__ = ["get_version"]


def get_version() -> str:
    """Return the installed version of the agents package if available."""
    try:
        return metadata.version("eternia")
    except metadata.PackageNotFoundError:
        return "0.0.0-dev"
