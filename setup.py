"""
Setup file for pygoodle
"""

from setuptools import find_packages, setup

from pygoodle import __version__

# Written according to the docs at
# https://packaging.python.org/en/latest/distributing.html

setup(
    name='pygoodle',
    description='General Python utils',
    version=__version__,
    url='https://github.com/JrGoodle/pygoodle',
    author='Joe DeCapo',
    license='MIT',
    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Developers'
    ],
    packages=find_packages(exclude=['tests.*']),
    install_requires=[
        'argcomplete',
        'colorama',
        'humanize',
        'jsonschema',
        'paramiko',
        'pick',
        'PyYAML',
        'resource_pool',
        'rich',
        'trio'
    ]
)
