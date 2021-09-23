from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in afs_integration/__init__.py
from afs_integration import __version__ as version

setup(
	name="afs_integration",
	version=version,
	description="AFS Payment Gateway",
	author="Tridz Technologies",
	author_email="info@tridz.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
