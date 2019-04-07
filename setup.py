from setuptools import setup, find_packages

TESTS_REQUIRE = ['pytest', 'mock', 'nose', 'coveralls']

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Database',
    'Topic :: Scientific/Engineering :: Astronomy'
]

LONG_DESCRIPTION = open('README.rst').read()

setup(
    name='PyOngc',
    version='0.3.1',
    author='Mattia Verga',
    author_email='mattia.verga@tiscali.it',
    url='https://github.com/mattiaverga/PyOngc',
    packages=find_packages(exclude=("tests",)),
    package_data={'pyongc': ['ongc.db', ], },
    license='MIT',
    description='Python interface to OpenNGC database data.',
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    install_requires=[
        'Click',
        'numpy',
    ],
    entry_points='''
        [console_scripts]
        ongc=pyongc.scripts.ongc:cli
    ''',
    tests_require=TESTS_REQUIRE,
    extras_require={'tests': TESTS_REQUIRE},
    python_requires=">=3",
)
