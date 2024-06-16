from setuptools import setup, find_packages

setup(
    name='stocklib',
    version='0.1',
    packages=find_packages(),
    description='A lib for stocks',
    long_description=open('README.md').read(),
    long_description_content_type='',
    author='Tiago Oliveira',
    author_email='tiagojgroliveira@tecnico.ulisboa.pt',
    url='https://github.com/GaspTO/stocks',
    install_requires=[
        # List all packages that your library needs to work
        'numpy',  # Just an example, replace it with actual dependencies
        'pandas',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',  # Change as appropriate
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',  # Assuming your library is MIT Licensed
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            # Enable this if your package contains scripts that should be accessible from the CLI
            # 'script_name = module_name:function_name',
        ],
    },
    keywords='your library keywords',  # Helps users find your library on PyPI
)

