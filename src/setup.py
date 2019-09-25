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
    name="woql-client-p",
    version="0.0.1",
    author="Francesca Bitto",
    author_email="francesca@datachemist.com",
    description="woql client for Terminus DB",
    long_description_content_type="woql client for DB",
    package_data={'': ['LICENSE']},
    url="https://github.com/terminusdb/woql-client-p",
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


