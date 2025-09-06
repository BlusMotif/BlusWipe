"""
Setup script for BlusWipe Production Application
Developed by Eleblu Nunana
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="bluswipe-production",
    version="1.0.0",
    author="Eleblu Nunana",
    description="AI-powered background removal service optimized for cloud deployment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi==0.116.1",
        "uvicorn[standard]==0.35.0",
        "python-multipart==0.0.20",
        "aiofiles==24.1.0",
        "jinja2==3.1.6",
        "Pillow==11.3.0",
        "numpy==2.2.6",
        "opencv-python-headless==4.12.0.88",
        "torch==2.8.0",
        "torchvision==0.23.0",
        "rembg==2.0.67",
        "gunicorn==23.0.0",
        "prometheus-fastapi-instrumentator==7.1.0",
        "python-dotenv==1.1.1",
        "httptools==0.6.4",
        "watchfiles==1.1.0",
        "websockets==15.0.1",
        "onnxruntime",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "black",
            "flake8",
            "mypy",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        "console_scripts": [
            "bluswipe=main:main",
        ],
    },
)
