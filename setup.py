from setuptools import setup, find_packages
import os

version = '1.4'

setup(name='collective.quickupload',
      version=version,
      description="Pure javascript files upload tool for Plone, with drag and drop, multi selection, and progress bar.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='Plone Multiple Files Upload',
      author='jean-mat Grimaldi',
      author_email='jeanmat.grimaldi@gmail.com',
      url='http://plone.org/products/collective.quickupload',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        ],
      extras_require={
        'test': ['plone.app.testing'],
        },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
