from setuptools import setup

setup(
    name='opie',
    version='0.0.1',
    author='Jake McGinty',
    author_email='me@jake.su',
    description=("A helping friend for the OP-1 synthesizer."),
    py_modules=['opie'],
    packages=['commands', 'helpers'],
    install_requires=[
        'Click',
        'pyusb'
    ],
    entry_points='''
        [console_scripts]
        opie=opie:cli
    ''',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ]
)
