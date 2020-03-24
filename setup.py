
import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name='dnac',
    version='1.3.1.6',
    author='Robert Sayle',
    author_email='rsayle@cisco.com',
    description='A wrapper for using Cisco DNA Center\'s REST API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://developer.cisco.com/codeexchange/github/repo/rsayle/DNAC-Python-Wrapper',
    packages=setuptools.find_packages(exclude=['docs', 'examples']),
    python_requires='>=3',
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Telecommunications Industry'
    ],
    install_requires=['requests', 'multi_key_dict']
)
