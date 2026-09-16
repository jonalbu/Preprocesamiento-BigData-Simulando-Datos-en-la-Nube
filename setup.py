from setuptools import setup, find_packages

setup(
    name="preprocessing-bigdata-ea2",
    version="1.0.0",
    description="EA2: Preprocesamiento y Limpieza de Datos en Plataforma de Big Data en la Nube",
    author="IU Digital de Antioquia - Jonathan Alvarez Bustamante",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.2.0",
        "openpyxl>=3.1.2",
        "numpy>=1.26.0",
        "scikit-learn>=1.4.0",
    ],
    python_requires=">=3.9",
)
