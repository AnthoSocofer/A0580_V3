from setuptools import setup, find_packages

setup(
    name="docusearch-agency",
    packages=find_packages(include=['app', 'app.*']),
)