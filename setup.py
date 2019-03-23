from setuptools import setup, find_packages


def read_file(name):
    with open(name) as fd:
        return fd.read()


setup(
    name='django-pivot',
    version='1.8.0',
    description='Create pivot tables and histograms from ORM querysets',
    long_description=read_file('README.rst'),
    url='https://github.com/martsberger/django-pivot',
    download_url='https://github.com/martsberger/django-pivot/archive/1.8.0.tar.gz',
    author='Brad Martsberger',
    author_email='bmarts@lumere.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=find_packages(),
    install_requires=['django>=1.10', 'six']
)
