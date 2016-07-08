from setuptools import setup

setup(
    name='opie',
    version='0.1',
    py_modules=['opie'],
    install_requires=[
        'Click',
        'pyusb'
    ],
    entry_points='''
        [console_scripts]
        opie=opie:cli
    ''',
)
