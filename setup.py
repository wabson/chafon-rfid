import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='wabson.chafon-rfid',
    version='0.0.4',
    author='Will Abson',
    author_email='will@wabson.org',
    description='Read RFID data from Chafon UHF readers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/wabson/chafon-rfid',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.4',
    extras_require={
        'test': []
    },
)
