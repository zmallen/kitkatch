#!/usr/bin/env python

from setuptools import setup

setup(name='kitkatch',
      version='0.1.0',
      description='Katch some phishing kits using YAML rules',
      author='Zack Allen',
      author_email='zma4580@gmail.com',
      url='https://www.github.com/zmallen/kitkatch',
      include_package_data=True,
      packages=['kitkatch'],
      entry_points = {
          'console_scripts': 'kitkatch=kitkatch.katch:main'
      },
#      install_requires=[
#      ],
     )
