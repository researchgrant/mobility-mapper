import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mobility-mapper",
    version="0.0.10",
    author="Grant Weiss",
    author_email="grant.weiss@me.com",
    description="For manually scoring mobility in behavior tests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/researchgrant/mobility-mapper/",
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'pandas', 'opencv-python','PyQt5','pyqtgraph'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)