import os

from setuptools import setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

exec(open('src/__init__.py').read())

setup(
    name='newrelicnfsmond',
    version=__version__,
    license='MIT License',
    description='NFS disk monitoring plugin for New Relic',
    author='Cody Kinsey',
    author_email='ckinsey@efolder.net',
    url='https://github.com/internetfett/newrelic-nfsmond',
    long_description='A plugin for New Relic to gather information on NFS disk space',
    packages=['newrelicnfsmond'],
    package_dir={'newrelicnfsmond': 'src'},
    scripts=['scripts/newrelic-nfsmond'],
    data_files=[
        ('/etc', ['conf/newrelic-nfsmond.conf']),
        ('/etc/init.d', ['scripts/init/newrelic-nfsmond']),
    ],
    install_requires=['python-daemon'],
    classifiers=[
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
