from setuptools import setup


setup(
    name='ociedoo',
    version='0.1.0',
    py_module=['ociedoo'],
    install_requires=[
        'sh',
    ],
    entry_points={
        'console_scripts': [
            'ociedoo = ociedoo.__main__:main',
        ]
    },
)
