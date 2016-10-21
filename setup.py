from setuptools import find_packages, setup


setup(
    name="heropets-webserver",
    version='2.0.0-dev0',
    packages=find_packages(),
    install_requires=[
        'tornado',
        'tornado-redis',
        'redis',
    ],
)
