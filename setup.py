from distutils.core import setup

CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Topic :: Database',
    'Topic :: Scientific/Engineering :: Astronomy'
]

LONG_DESCRIPTION = open('README').read()

setup(
    name='PyOngc',
    version='0.1.1',
    author='Mattia Verga',
    author_email='mattia.verga@tiscali.it',
    url='https://github.com/mattiaverga/PyOngc',
    packages=['pyongc',],
    package_data={'pyongc': ['ongc.db',],},
    scripts=['bin/ongcbrowse',],
    license='MIT',
    description='Python interface to OpenNGC database data.',
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
)
