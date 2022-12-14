from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in al_ansari/__init__.py
from al_ansari import __version__ as version

setup(
	name="al_ansari",
	version=version,
	description="Al Ansari Trading Enterprises LLC",
	author="Indictrans",
	author_email="neha.t@indictranstech.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
