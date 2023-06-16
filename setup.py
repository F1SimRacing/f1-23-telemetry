import setuptools
import f1_23_telemetry

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='f1-23-telemetry',
    version=f1_23_telemetry.__version__,
    author='Chris Hannam',
    author_email='ch@chrishannam.co.uk',
    description='Decode F1-23 telemetry data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chrishannam/f1-23-telemetry',
    packages=setuptools.find_packages(exclude=('tests', 'examples')),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'telemetry-f1-2022-recorder=f1_22_telemetry.main:main',
        ]
    },
    include_package_data=True,
    python_requires='>=3.7',
)
