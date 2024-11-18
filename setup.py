from setuptools import setup, find_packages
import os


def load_requirements(filename='requirements.txt'):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]


install_requires = load_requirements('requirements.txt')
setup(
    name='Disbrava Reports',
    version='1.0',
    install_requires=install_requires,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'run-application=app.main:main',  # Replace with the actual path
        ],
    },
)
