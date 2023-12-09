#  Generate wheel file:
#
#  python3 -m pip install setuptools wheel
#  python3 setup.py bdist_wheel


from setuptools import setup

setup ( 

name                          = "konto",
version                       = "0.0.1",
packages                      = ['.konto'],
author                        = "Christian Martin Gabriel",
author_email                  = "christian.gabriel@ift-informatik.de",
url                           = "https://github.com/cgabr/konto",
description                   = "A Python Library for Accounting",

python_requires               = '>=3.6',
long_description_content_type = "text/markdown",
long_description              = open("README.md").read()


)

