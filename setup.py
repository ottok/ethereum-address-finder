from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='Ethereum address finder',
    ext_modules=cythonize("ethaddrfinder.py", language_level="3"),
)

# Build with:
#   python3 setup.py build_ext --inplace
#
# Run with:
#   python3 ethaddrfinder-cython.py
