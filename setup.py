from setuptools import find_packages, setup


with open('README.md') as file:
    long_description = file.read()


setup(
    name='manimutils',
    description='My personal utilities for working with manim and manim-slides',
    version='0.1.0',
    author='Cameron Churchwell',
    author_email='cc178@illinois.edu',
    url='https://github.com/cameronchurchwell/manimutils',
    install_requires=[
        'manim', # 0.19.0
        'manim-slides', # 5.4.2
        'numpy',
    ],
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['manim'],
    classifiers=['License :: OSI Approved :: MIT License'],
    license='MIT')