from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("qa-kit-cli")
except PackageNotFoundError:
    __version__ = "0.4.1"
