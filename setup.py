from setuptools import setup

setup(
    entry_points={
        "spey.backend.plugins": ["example.poisson = example_poisson:PoissonPDF"]
    }
)
