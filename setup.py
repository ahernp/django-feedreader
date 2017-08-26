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
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django==1.11.4',
        'django-braces==1.11.0',
        'factory-boy==2.9.2',
        'feedparser==5.2.1',
        'mock==2.0.0',
        'pytz==2017.2',
    ],
)
