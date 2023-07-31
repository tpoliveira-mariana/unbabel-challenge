from setuptools import setup

setup(
    name='maverage',
    version='0.1.0',
    py_modules=['moving_average'],
    install_requires=[
        'Click',
        'pandas',
    ],
    entry_points={
        'console_scripts': [
            'maverage = moving_average:process_events',
        ],
    },
)

# pip install --editable .