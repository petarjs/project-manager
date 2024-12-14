"""
Setup script for creating a macOS application bundle.
"""
from setuptools import setup, find_packages

APP = ['src/project_manager/__main__.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,  # This makes it a status bar app
        'CFBundleName': 'Project Manager',
        'CFBundleDisplayName': 'Project Manager',
        'CFBundleIdentifier': 'com.cursor.projectmanager',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
    },
    'packages': [
        'rumps',
        'PIL',
        'psutil',
        'pymysql',
        'tkinter',
    ],
    'includes': [
        'pkg_resources',
        'packaging',
        'packaging.version',
        'packaging.specifiers',
        'packaging.requirements'
    ],
    'excludes': [
        'setuptools',
        'pip',
        'wheel'
    ],
    'iconfile': 'src/project_manager/assets/icon.png',
    'resources': ['src/project_manager/assets'],
    'strip': True,
    'semi_standalone': False,
}

setup(
    name="project_manager",
    version="0.1.0",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'rumps>=0.4.0',
        'pillow>=10.1.0',
        'psutil>=5.9.0',
        'pymysql>=1.1.0'
    ]
) 