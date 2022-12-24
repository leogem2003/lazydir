from setuptools import setup, find_packages

setup(
    name='lazydir',
    version='1.0.0',
    py_modules=find_packages(),
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'lazydir = lazydir.cli:cli',
        ],
    },
)
