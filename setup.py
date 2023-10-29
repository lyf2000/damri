from setuptools import find_packages, setup

setup(
    name="damri",
    version="0.1.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django",
        "drf-spectacular",
        "djangorestframework",
        "pydantic",
    ],
)
