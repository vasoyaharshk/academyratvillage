import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="academy",
    version="0.0.1",
    author="Rafael Marín, Juan Garrido",
    author_email="marinraf@gmail.com, garridooliverjuan@gmail.com",
    description="Package to train animals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://delaRochaLab@bitbucket.org/delaRochaLab/academy.git",
    # install_requires=['pyserial', 'pandas', 'numpy', 'psychopy'],
    include_package_data=True,
    packages=setuptools.find_packages(),
    data_files=[],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['academy=academy.__main__:main']
    }
)
