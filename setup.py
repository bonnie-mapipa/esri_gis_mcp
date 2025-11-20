#!/usr/bin/env python3
"""
Setup script for eThekwini ESRI GIS MCP Server
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "eThekwini ESRI GIS Model Context Protocol Server"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return [
        "mcp>=1.0.0",
        "httpx>=0.25.0",
        "asyncio-mqtt>=0.13.0",
    ]

setup(
    name="ethekwini-gis-mcp",
    version="1.0.0",
    description="eThekwini ESRI GIS Model Context Protocol Server",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Bongiwe Mapipa",
    author_email="bongiwemapipa82@gmail.com",
    url="https://github.com/bonnie-mapipa/ethekwini-gis-mcp",
    project_urls={
        "Bug Reports": "https://github.com/bonnie-mapipa/ethekwini-gis-mcp/issues",
        "Source": "https://github.com/bonnie-mapipa/ethekwini-gis-mcp",
        "Documentation": "https://github.com/bonnie-mapipa/ethekwini-gis-mcp/blob/main/README.md",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-asyncio>=0.20.0",
            "coverage>=6.0",
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Database :: Database Engines/Servers",
    ],
    keywords=[
        "mcp", "model-context-protocol", "gis", "esri", "ethekwini", 
        "arcgis", "spatial-data", "geospatial", "municipal-data", 
        "open-data", "rest-api"
    ],
    entry_points={
        "console_scripts": [
            "ethekwini-gis-mcp=ethekwini_gis_mcp:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)