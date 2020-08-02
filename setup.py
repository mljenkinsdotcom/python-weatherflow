'''
setup.py is the build script for setuptools. It tells setuptools about your package (such as the name and version) as well as which code files to include.

Open setup.py and enter the following content. Update the package name to include your username (for example, example-pkg-theacodes), this ensures that you have a unique package name and that your package doesn’t conflict with packages uploaded by other people following this tutorial.
# https://packaging.python.org/tutorials/packaging-projects/
'''
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="weatherflow", # Replace with your own username
    version="0.0.1",
    author="Matthew Jenkins",
    author_email="matt@mljenkins.com",
    description="Library to interact with WeatherFlow APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mljenkinsdotcom/python-weatherflow",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)