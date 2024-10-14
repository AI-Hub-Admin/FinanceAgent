from setuptools import setup, find_packages
import pathlib

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="FinanceAgent",  
    version="0.0.2",    
    description="Open API of realtime financial Market data, including Stock Price Quote from Global Market US Europe Asia, Major Index Dow/Nasdaq/S&P/Hang Seng/Nifty50, etc.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author_email="aihubadmin@126.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="API,Finance,AI Agent",
    packages=find_packages(where="src"),
    package_dir={'': 'src'},
    python_requires=">=3.4",
    project_urls={
        "homepage": "http://www.deepnlp.org",
        "repository": "https://github.com/AI-Hub-Admin/FinanceAgent"
    },
)
