from setuptools import setup, find_packages
import os, sys, glob, fnmatch

setup(name="summarize",
  version=0.1,
  author='Vighnesh Birodkar,Dhruv Jawali',
  packages = find_packages(),
  package_data  = { #DO NOT REMOVE, NEEDED TO LOAD INLINE FILES i = Image('simplecv')
            'summarize': ['Visualize/*.js',
                        'Visualize/*.pde',
                        'Visualize/*.html',
                        ]
  },


  )
