import setuptools

setuptools.setup(
    name="woql-client-p",
    version="0.0.1",
    author="Francesca Bitto",
    author_email="francesca@datachemist.com",
    description="woql client for Terminus DB",
    long_description_content_type="text/markdown",
    url="https://github.com/terminusdb/woql-client-p",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: APACHE 2",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

requires = [
   'requests',
   'setuptools'

]
test_requirements = [
    'pytest>=3'
]