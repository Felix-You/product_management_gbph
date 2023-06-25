import os

from distutils.core import setup, Extension
import base64, pyDes
from Cython.Build import cythonize

py_files = ['Encrypt.pyx', ]

setup(ext_modules=cythonize(py_files), )

# setup(ext_modules = cythonize(Extension(
#     'Encrypt',
#     sources=['registration/Encrypt.pyx'],
#     language='c',
#     include_dirs=[],
#     library_dirs=[],
#     libraries=[],
#     extra_compile_args=[],
#     extra_link_args=[]
# )))
