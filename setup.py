# setup.py

from setuptools import setup, find_packages

setup(
    name='blackjack_simulator',
    version='1.0.0',
    description='A blackjack tournament simulator with adjustable player aggressiveness.',
    author='Kresimir Sparavec',
    author_email='ksparavec@devitops.com',
    url='https://github.com/ksparavec/blackjack_simulator',
    packages=find_packages(),
    install_requires=[
        'PyYAML>=5.1'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
