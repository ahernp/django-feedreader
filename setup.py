import os
from setuptools import setup

import feedreader

version = feedreader.__version__
long_description = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name = 'django-feedreader',
    version = version,
    packages = ['feedreader'],
    include_package_data = True,
    license = 'BSD License',
    description = 'A simple Django app to aggregate RSS feeds.',
    long_description = long_description,
    url = 'https://github.com/ahernp/django-feedreader',
    author = 'Paul Ahern',
    author_email = 'ahernp@ahernp.com',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'Django==2.0.3',
        'django-braces==1.12.0',
        'factory-boy==2.10.0',
        'feedparser==5.2.1',
    ],
)
