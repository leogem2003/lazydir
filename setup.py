from setuptools import setup, find_packages

setup(
    name='fileconsole',
    version='0.1.0',
    py_modules=find_packages(),
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'fileconsole = fileconsole.cli:cli',
        ],
    },
)
