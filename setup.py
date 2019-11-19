import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="package-delivery-app",
    version="0.9.0",
    author="Adam Isom",
    author_email="adam.r.isom@gmail.com",
    description="A simulation of package delivery with constraints",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adamisom/package-delivery-app",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6.8',
)
