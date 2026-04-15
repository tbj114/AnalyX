import PyInstaller.__main__
import os
import sys

def build():
    PyInstaller.__main__.run([
        'src/main.py',
        '--name=AnalyX',
        '--windowed',
        '--onefile',
        '--icon=NONE',
        '--add-data', 'src:src',
        '--hidden-import', 'numpy',
        '--hidden-import', 'pandas',
        '--hidden-import', 'scipy',
        '--hidden-import', 'matplotlib',
        '--hidden-import', 'seaborn',
        '--hidden-import', 'openpyxl',
        '--hidden-import', 'pyreadstat',
        '--hidden-import', 'PyQt6',
        '--hidden-import', 'PyQt6.QtCore',
        '--hidden-import', 'PyQt6.QtGui',
        '--hidden-import', 'PyQt6.QtWidgets',
        '--collect-all', 'numpy',
        '--collect-all', 'pandas',
        '--collect-all', 'scipy',
        '--collect-all', 'matplotlib',
        '--collect-all', 'PyQt6',
        '--clean',
        '--noconfirm',
    ])

if __name__ == '__main__':
    build()
