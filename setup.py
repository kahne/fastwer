# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys


class PyBind11Helper(object):
    def __init__(self, user: bool = False):
        self.user = user

    def get_include(self):
        import pybind11
        return pybind11.get_include(self.user)


ext_modules = [
    Extension(
        'fastwer',
        ['src/fastwer.cpp', 'src/bindings.cpp'],
        include_dirs=[PyBind11Helper().get_include(), PyBind11Helper(user=True).get_include()],
        language='c++',
    ),
]


# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14/17] compiler flag.
    The newer version is prefered over c++11 (when it is available).
    """
    flags = ['-std=c++17', '-std=c++14', '-std=c++11']

    for flag in flags:
        if has_flag(compiler, flag): return flag

    raise RuntimeError('Unsupported compiler -- at least C++11 support is needed!')


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }
    l_opts = {
        'msvc': [],
        'unix': [],
    }

    if sys.platform == 'darwin':
        darwin_opts = ['-stdlib=libc++', '-mmacosx-version-min=10.14']
        c_opts['unix'] += darwin_opts
        l_opts['unix'] += darwin_opts

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
        for ext in self.extensions:
            ext.extra_compile_args = opts
            ext.extra_link_args = link_opts
        build_ext.build_extensions(self)


if sys.version_info < (3, 6):
    sys.exit('Sorry, Python >= 3.6 is required.')

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_content = f.read()

with open('VERSION') as f:
    version = f.read()

setup(
    name='fastwer',
    version=version,
    author='Changhan Wang',
    author_email='wangchanghan@gmail.com',
    description='A PyPI package for fast word/character error rate (WER/CER) calculation',
    url='https://github.com/kahne/fastwer',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    setup_requires=['setuptools>=18.0', 'pybind11'],
    ext_modules=ext_modules,
    packages=['fastwer'],
    package_dir={'fastwer': 'src'},
    # data_files=[('', ['VERSION', 'LICENSE'])],
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
)
