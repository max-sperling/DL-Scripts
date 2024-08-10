from setuptools import setup, find_packages

setup(
    name="dl-scripts",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'playlist_downloader=apps.playlist_downloader:main',
            'pattern_downloader=apps.pattern_downloader:main'
        ]
    },
)
