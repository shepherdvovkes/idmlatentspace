from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sysex-toolkit",
    version="1.0.0",
    author="SystematicLabs",
    author_email="ovcharov@systematiclabs.com",
    description="Universal SysEx decoder/encoder library for synthesizers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SystematicLabs/sysex-toolkit",
    project_urls={
        "Bug Tracker": "https://github.com/SystematicLabs/sysex-toolkit/issues",
        "Documentation": "https://github.com/SystematicLabs/sysex-toolkit/wiki",
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'sysex_toolkit': ['configs/*.json', 'configs/*.yaml'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Artistic Software",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest>=6.0", "black>=21.0", "flake8>=3.8", "mypy>=0.812"],
        "examples": ["matplotlib>=3.3.0", "librosa>=0.8.0"],
        "ml": ["scikit-learn>=1.0.0", "tensorflow>=2.6.0"],
    },
    entry_points={
        "console_scripts": [
            "sysex-decode=sysex_toolkit.cli:decode_command",
            "sysex-encode=sysex_toolkit.cli:encode_command", 
            "sysex-analyze=sysex_toolkit.cli:analyze_command",
        ],
    },
    keywords="sysex, synthesizer, midi, audio, music production, access virus, roland",
)

