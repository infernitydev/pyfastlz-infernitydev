from setuptools import setup, Extension

setup(
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    ext_modules=[
        Extension(
            'fastlz',
            sources=['fastlz.c', 'fastlz/fastlz.c'],
            include_dirs=['fastlz']
        )
    ],
)
