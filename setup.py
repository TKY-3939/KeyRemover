from setuptools import setup

setup(
    name="KeyRemover",
    version="1.0.0",
    description="A tool to completely remove macOS applications and reset trial periods",
    author="KeyRemover Team",
    author_email="info@keyremover.com",
    url="https://github.com/keyremover/keyremover",
    py_modules=["key_remover", "key_remover_gui"],
    install_requires=[
        "PyQt5>=5.15.0",
    ],
    entry_points={
        'console_scripts': [
            'keyremover=key_remover:main',
        ],
        'gui_scripts': [
            'keyremover-gui=key_remover_gui:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
) 