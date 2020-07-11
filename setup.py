from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()


setup(
    author="James O'Beirne",
    author_email='james.obeirne@pm.me',
    python_requires='>=3.7',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="function annotations -> cli",
    license="MIT license",
    include_package_data=True,
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords='clii',
    name='clii',
    packages=find_packages(),
    url='https://github.com/jamesob/clii',
    version='0.2.2',
)
