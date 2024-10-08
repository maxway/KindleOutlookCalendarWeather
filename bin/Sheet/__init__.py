"""
A simple python library to interact with Google Sheet & Vika sheet API
"""

# import warnings
# import sys

# from .googlesheet import GoogleSheet
from .vikasheet import VikaSheet

__version__ = VikaSheet.__version__

# if sys.warnoptions:
#     # allow Deprecation warnings to appear
#     warnings.simplefilter('always', DeprecationWarning)
