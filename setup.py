import pathlib

# python 3.9 is required.
try:
    # Use setup() from setuptools(/distribute) if available
    from setuptools import setup
except ImportError:
    from distutils.core import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

from Simple_Process_REPL import __version__

setup(
    name="Simple_Process_REPL",
    version=__version__,
    # Your name & email here
    long_description=README,
    long_description_content_type="text/markdown",
    description="An extensible application framework with REPL for creating processes with side effects.",
    url="https://github.com/EricGebhart/Simple_Process_REPL",
    author="Eric Gebhart",
    author_email="e.a.gebhart@gmail.com",
    packages=["Simple_Process_REPL"],
    include_package_data=True,
    package_data={"": ["*.yaml", "*.spr", "*.txt"]},
    scripts=[],
    license="MIT",
    entry_points={"console_scripts": ["SPR=Simple_Process_REPL.__main__:main"]},
    install_requires=[
        "pyserial",
        "pythondialog",
        "pyYAML",
        "regex",
        "python-barcode",
        "qrcode",
        "Pillow",
        "opencv-python",
        "numpy",
        "Image",
        "Pyzbar",
        "markdown"
        # "brother_ql",
    ],
)
