import setuptools

requires = [
   'requests'
]

test_requirements = [
    'pytest>=3',
    'pytest-cov',
    'pytest-mock',
    'pytest-xdist',
]

setuptools.setup(
    name="terminus-client-python",
    version="0.0.1",
    author="Francesca Bitto",
    author_email="francesca@datachemist.com",
    description="woql client for Terminus DB",
    long_description_content_type="terminus client for DB",
    package_data={'': ['LICENSE']},
    url="https://github.com/terminusdb/terminus-client-python",
    packages=setuptools.find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=requires,
   
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: APACHE 2",
        "Operating System :: OS Independent",
    ],
    setup_requires=['pytest-runner'],
    tests_require=test_requirements,
    python_requires='>=3.6',
)


