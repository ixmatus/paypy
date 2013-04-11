import sys
from setuptools import setup, find_packages

version = '0.6'

if not '2.5' <= sys.version < '3.0':
    raise ImportError('Python version not supported')

tests_require = ['nose']

setup(name="PayPy",
      version=version,
      install_requires=['lxml >= 2.2.8', 'zope.schema >= 3.7.0'],
      
      description="Payment gateway API integration package",
      long_description="""\
Paypy simplifies payment gateway interaction by homogenizing the 
programming interface for multiple providers.

It has a `mercurial repository
<https://ixmatus@bitbucket.org/ixmatus/paypy>`_ that
you can install from with ``easy_install paypy``

""",
      classifiers=["Intended Audience :: Developers",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Parnell Springmeyer",
      author_email="ixmatus@gmail.com",
      url="http://bitbucket.org/ixmatus/paypy",
      license="PSF",
      zip_safe=False,
      packages=find_packages(),
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=tests_require
      )
