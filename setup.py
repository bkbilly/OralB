import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='oralb',
    version='0.1.3',
    author="bkbilly",
    author_email="bkbilly@hotmail.com",
    description="Connect to an OralB toothbrush via Bluetooth",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bkbilly/oralb",
    packages=setuptools.find_packages(),
    install_requires=[
        'bleak>=0.18.1'
        'bleak-retry-connector>=2.1.3',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
 )
