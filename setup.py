from setuptools import find_packages, setup

setup(
    name="damri",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "django",
        "drf-spectacular",
        "djangorestframework",
        "pydantic",
    ],
)
