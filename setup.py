from setuptools import setup, find_packages

setup(
    name='CyberXNoteloom',
    version='0.1.0',
    author='Haykel Yousfi',
    author_email='cyberxtech.haykel@outlook.com',
    description='A fully optimized MIDI-to-Multi-Format Audio Converter with advanced synthesis, DSP effects, and musical notation support.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/HKLYousfi/CyberXNoteloom',
    packages=find_packages(),
    install_requires=[
        'mido',
        'numpy',
        'pyFLAC',
        'lameenc',
        'scipy',
        'soundfile',
        'python-docx'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    entry_points={
        'console_scripts': [
            'cyberxnoteloom=cli.main:main',
        ],
    },
)
