#!/usr/bin/env python3
"""
Setup script for FRP Freedom Android
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="frp-freedom-android",
    version="1.0.0",
    author="FRP Freedom Project",
    description="FRP Freedom - Android APK for FRP Bypass",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frp-freedom/frp-freedom-android",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "flet>=0.21.0",
        "jnius>=1.1.0",
        "pyyaml>=6.0",
        "cryptography>=41.0.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "frp-freedom=frp_freedom_android.android_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "frp_freedom_android": ["assets/*", "assets/*/*"],
    },
)
