import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-ses-plus',
    version='1.0.0',
    packages=['django_ses_plus'],
    include_package_data=True,
    install_requires=['Django >= 3.2', 'django-ses >= 1.0.0', 'celery >= 4'],
    license='Apache-2.0',
    description="It's a Django module to store and send email with AWS SES.",
    long_description=README,
    long_description_content_type="text/markdown",
    author='hipo',
    author_email='pypi@hipolabs.com',
    url='https://github.com/Hipo/django-ses-plus',
    python_requires=">=3.6",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
