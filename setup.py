from setuptools import setup, find_packages

setup(
    name="smart_code_review",
    version="1.0.0",
    description="Parallel Multi-Agent Code Review System",
    author="Smart Code Review Team",
    packages=find_packages(),
    install_requires=[
        "langgraph>=0.0.10",
        "google-generativeai>=0.3.0",
        "requests>=2.25.0",
        "pylint>=2.8.0",
        "pytest>=6.0.0",
        "pytest-cov>=2.12.0",
    ],
    entry_points={
        "console_scripts": [
            "code-review=smart_code_review.main:main",
        ],
    },
)