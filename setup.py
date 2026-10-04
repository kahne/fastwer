# MIT License
# Copyright (c) 2020 Changhan Wang (wangchanghan@gmail.com)

import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import os
import sys
import pybind11


ext_modules = [
    Extension(
        'fastwer',
        ['src/fastwer.cpp', 'src/bindings.cpp'],
        include_dirs=[pybind11.get_include()],
        language='c++',
    ),
]


def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    # NamedTemporaryFile is held open on Windows, so use delete=False
    # and clean up manually to avoid file-lock errors.
    tmp = tempfile.NamedTemporaryFile('w', suffix='.cpp', delete=False)
    try:
        tmp.write('int main (int argc, char **argv) { return 0; }')
        tmp.close()
        try:
            compiler.compile([tmp.name], extra_postargs=[flagname])
        except setuptools.errors.CompileError:
            return False
        return True
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


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

    def run(self):
        super().run()
        # This project exposes a top-level extension module rather than a
        # package. Setuptools does not automatically place top-level .pyi
        # files next to extension modules, so copy the stub into the wheel's
        # import directory explicitly.
        self.copy_file('fastwer.pyi', os.path.join(self.build_lib, 'fastwer.pyi'))
        # PEP 561 marker for typed package
        typed_src = 'py.typed'
        if os.path.exists(typed_src):
            self.copy_file(typed_src, os.path.join(self.build_lib, 'py.typed'))

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO=%s' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
            if has_flag(self.compiler, '-O3'):
                opts.append('-O3')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=%s' % self.distribution.get_version())
            opts.append('/O2')
        for ext in self.extensions:
            ext.extra_compile_args = opts
            ext.extra_link_args = link_opts
        build_ext.build_extensions(self)


if sys.version_info < (3, 8):
    sys.exit('Sorry, Python >= 3.8 is required.')

with open('README.md') as f:
    readme = f.read()

with open('VERSION') as f:
    version = f.read().strip()

setup(
    name='fastwer',
    version=version,
    author='Changhan Wang',
    author_email='wangchanghan@gmail.com',
    description='A PyPI package for fast word/character error rate (WER/CER) calculation',
    url='https://github.com/kahne/fastwer',
    project_urls={
        'Issues': 'https://github.com/kahne/fastwer/issues',
        'Source': 'https://github.com/kahne/fastwer',
    },
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: C++',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Operating System :: OS Independent',
    ],
    keywords='wer cer asr speech-recognition evaluation',
    python_requires='>=3.8',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
)
