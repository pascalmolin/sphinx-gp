# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import io
def readfile(filename):
    with io.open(filename, encoding="utf-8") as stream:
        return stream.read().split("\n")

readme = readfile("README.rst")[5:]  # skip title and badges
version = readfile("VERSION")[0].strip()

requires = ['Sphinx>=0.6']

setup(
    name='sphinx-gp',
    version='0.1',
    url='https://github.com/pascalmolin/sphinx-gp',
    license='MIT',
    author='Pascal Molin',
    author_email='molin.maths@gmail.com',
    description=readme[0],
    long_description="\n".join(readme[2:]),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Sphinx :: Extension',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
