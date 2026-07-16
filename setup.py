from setuptools import setup, find_packages

setup(
    name="nmr-simple-plotter",
    version="0.1.0",
    description="Config-driven NMR data processing and plotting tool for publication-quality figures",
    author="Fionn Ferreira",
    author_email="fionn.ferreira@phys.chem.ethz.ch",
    url="https://github.com/fionnf/nmr-simple-plotter",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21",
        "scipy>=1.7",
        "matplotlib>=3.5",
        "pydantic>=2.0",
        "PyYAML>=6.0",
        "h5py>=3.0",
        "click>=8.0",
        "tqdm>=4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
        ],
        "reports": [
            "plotly>=5.0",
            "reportlab>=4.0",
            "markdown>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nmr-plotter=nmr_plotter.plotter:main",
        ],
    },
)
