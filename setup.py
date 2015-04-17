from setuptools import setup, find_packages

setup(
    name = "beets-copyartifacts",
    version = "0.1.2",
    description="beets plugin to copy non-music files to import path",
    long_description=open('README.rst').read(),
    author='Sami Barakat',
    author_email='sami@sbarakat.co.uk',
    url='https://github.com/sbarakat/beets-copyartifacts',
    download_url='https://github.com/sbarakat/beets-copyartifacts.git',
    license='MIT',

    packages=['beetsplug'],
    namespace_packages=['beetsplug'],
    install_requires = ['beets>=1.3.7']
)
