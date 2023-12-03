from setuptools import setup, find_packages

setup(
    name='lazydir',
    version='1.1.0',
    py_modules=find_packages('lazydir'),
    packages=['lazydir'],
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'lazydir = lazydir.cli:cli',
        ],
    },
)
