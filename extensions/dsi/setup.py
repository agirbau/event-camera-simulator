import numpy
from setuptools import setup, Extension
from Cython.Build import cythonize

print('Test1')

c_ext = Extension("dsi",
                  sources=["./src/cpp/code.cpp"],
                  language="c++",
                  include_dirs=[numpy.get_include()],
                  extra_compile_args=['-std=c++17'])

setup(
    name='dsi',
    version='0.0.1',
    description='Test cpp code',
    ext_modules=cythonize([c_ext])
)
