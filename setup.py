from setuptools import find_packages, setup

setup(
    name="aiorchestrator",
    version="0.1.0",
    description="AI-powered task orchestrator with memory management",
    author="Junior Amaya",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.8",
        "sqlalchemy>=2.0.38",
        "pytest>=8.3.4",
        "pytest-cov>=6.0.0",
        "jsonschema>=4.0.0",
        "pathlib>=1.0.1",
        "typing-extensions>=4.6.0",
        "colorama>=0.4.6",  # For Windows color support
        "python-dotenv>=1.0.0",  # For environment variables
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "mypy",
            "isort",
        ],
        "test": [
            "pytest-asyncio",
            "pytest-mock",
            "coverage",
        ],
    },
    entry_points={"console_scripts": ["aiorch=aiorchestrator.cli:cli"]},
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Source": "https://github.com/yourusername/aiorchestrator",
        "Bug Reports": "https://github.com/yourusername/aiorchestrator/issues",
        "Documentation": "https://aiorchestrator.readthedocs.io/",
    },
)
