import os

from setuptools import setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

exec(open('src/__init__.py').read())

setup(
    name='newrelic-nfsmond',
    version=__version__,
    license='MIT License',
    description='NFS disk monitoring plugin for New Relic',
    author='Cody Kinsey',
    author_email='internetfett@gmail.com',
    url='https://github.com/internetfett/newrelic-nfsmond',
    long_description='A plugin for New Relic to gather information on NFS disk space',
    packages=['newrelic-nfsmond'],
    package_dir={'newrelic-nfsmond': 'src'},
    classifiers=[
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
