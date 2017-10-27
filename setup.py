from setuptools import setup, find_packages

setup(
    name='django-pivot',
    version='1.6',
    description='Create pivot tables and histograms from ORM querysets',
    url='https://github.com/martsberger/django-pivot',
    download_url='https://github.com/martsberger/django-pivot/archive/1.6.tar.gz',
    author='Brad Martsberger',
    author_email='bmarts@procuredhealth.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    packages=find_packages(),
    install_requires=['django>=1.10']
)
