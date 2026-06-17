from setuptools import setup, find_packages
from Cython.Build import cythonize

extensions = cythonize(
    ["src/mvp_lite/**/*.py"],
    exclude=["**/__init__.py"],
    compiler_directives={"language_level": "3"},
)

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    ext_modules=extensions,
)