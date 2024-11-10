from setuptools import setup

setup(
    name='Disbrava Reports',
    version='1.0',
    packages=['email_context'],
    entry_points={
        'console_scripts': [
            'run-email_context=email_context.main:main',  # Replace with the actual path
        ],
    },
)
