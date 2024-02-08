from setuptools import setup, Extension

setup(
    ext_modules=[
        Extension(
            'fastlz',
            sources=['fastlz.c', 'fastlz/fastlz.c'],
            include_dirs=['fastlz']
        )
    ],
)
