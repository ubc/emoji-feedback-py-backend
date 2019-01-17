import setuptools
import os

long_description = 'Caliper emitting backend for the emoji feedback library'
if os.path.exists('README.md'):
    with open('README.md', 'r') as fh:
        long_description = fh.read()

setuptools.setup(
    name='emoji-feedback-py-backend',
    version='0.1.0',
    author='UBC Learning Analytic',
    author_email='justin.lee@ubc.ca',
    license='MIT License',
    url='https://github.com/ubc/emoji-feedback-py-backend',
    description='Caliper emitting backend for the emoji feedback library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['caliper', 'emoji', 'feedback', 'ubc'],
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    install_requires=[
        'requests>=v2.19.1'
    ],
    tests_require=[
        'nose',
        'mock',
        'coverage'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Education",
    ],
)