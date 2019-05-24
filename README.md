[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/rsayle/DNAC-Python-Wrapper)

# DNAC-Python-Wrapper
A python wrapper for easily accessing a Cisco DNA Center (DNAC) cluster.

# Purpose
The modules herein simplify placing calls to Cisco's DNA Center.  They handle all the complexity involved with making CRUD calls to Cisco DNAC including:
  - Automatically logging in and getting an XAuth token
  - Formatting URLs and filters to control requests to Cisco DNAC
  - Parsing responses from Cisco DNAC and converting from json text into python objects

# Installation and Usage
In addition to the source files available through Cisco DevNet and GitHub, the Cisco DNAC wrapper may be installed from the [distribution package on PiPy.](https://pypi.org/project/dnac/)

First, use the command _pip install dnac_ to download the package and install it in your python site package listing.

Then, edit the wrapper's configuration file, _dnac_config.py_, with your Cisco DNA Center cluster information.  Look in the directory _python-root-dir/Lib/site-packages/dnac/_ for the configuration file.

After installing the wrapper, import the Dnac class directly from the package but treat the various API modules as sub-packages.  For example:

    from dnac import Dnac
    
    d = Dnac()
    
    from dnac.networkdevice import NetworkDevice
    
    switch = NetworkDevice(d, "mySwitch")

# Versioning
In order to remain consistent with Cisco's DNA Center release cycle, this package follows a similar versioning structure.  Simply stated, the format is _Cisco-DNAC-version.wrapper-version_.  Take for example, release 1.2.10.2 of this package.  1.2.10 refers to the version of Cisco DNA Center which the package was tested against, and .2 indicates the version of the wrapper itself.

# License
This project is licensed by Cisco Systems according to the terms stated in the project's [LICENSE](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/LICENSE) file.

# Modules
- [__init__.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/__init__.py): Contains the base Dnac class and controls the dnac package.
- [dnac_config.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/dnacapi.py): Configuration file for instantiating a Dnac object.
- [basicauth.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/basicauth.py): HTTP basic authentication class, BasicAuth, used by Dnac to perform a login.
- [xauthtoken.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/xauthtoken.py): X-auth-token class, XAuthToken, used by Dnac to authorize commands after a successful login.
- [crud.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/crud.py): Crud class provides generic GET, PUT, POST and DELETE functions and is wrapped by DnacApi.
- [dnacapi.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/dnacapi.py): DnacApi virtual class from which all API calls inherit.
- [networkdevice.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/networkdevice.py): Manages devices in Cisco DNA Center, e.g. routers, switches, WLCs.
- [commandrunner.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/commandrunner.py): Runs read-only, i.e. show commands, on Cisco DNA Center.
- [task.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/task.py): Manages tasks executing on Cisco DNAC.
- [file.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/file.py): Retrieves the output created by completed tasks.
- [template.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/template.py): Manages CLI templates.
- [deployment.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/deployment.py): Monitors the progress of applying a CLI template to a network device.
- [client.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/client.py): Retrieves a client's state from Cisco DNAC for the time specified.
- [site.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/site.py): Pulls a site's state from Cisco DNAC for the time given.
- [timestamp.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/dnac/timestamp.py): Converts the system's time in UTC into milliseconds for pulling client and site state information from Cisco DNA Center.


# Examples
- [networkdevice_example.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/examples/networkdevice_example.py): An example script that shows how to use a NetworkDevice object.
- [commandrunner_example.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/examples/commandrunner_example.py): An example script showing how to use the CommandRunner class.
- [template_example.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/examples/template_example.py): An example script demonstrating how to use the Template class.

# Documentation
Detailed documentation for each module, its classes, attributes and functions can be found in [this project's HTML files](https://github.com/rsayle/DNAC-Python-Wrapper/tree/1.2.10.2/docs) or the docstrings contained within the modules themselves as well as in [Cisco DNA Center References](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-platform-overview/cisco-dna-center-platform-overview).

A summary diagram of the class hierarchy and their inter-relationships can be found in file [Cisco DNAC Wrapper UML](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/docs/Cisco%20DNAC%20Wrapper%20UML.pdf).

# Current State
v.1.2.10.2: 24 May 2019
- Added client, site, and timestamp classes
- Fixed various defects
- Adjusted template class to handle behavior changes from 1.2.8 to 1.2.10

# Roadmap
- Move unit test code from being embedded in modules to a test package structure.
- More enhancements to networkdevice
- Interface class

# History
v.1.2.10.1: 13 Mar 2019
- Completed packaging for distribution on PiPy and renamed the package to 'dnac'.
- Updated README.

v.1.2.10.0: 7 Mar 2019
- Modified version numbering to match Cisco DNA Center release cycle.
- Most attributes are now protected (read-only) with only a handful being private or public.
- Changed TaskResults class to File class in order to match Cisco DNAC's schema.
- Moved documentation and examples into subpackages.
- Added setuptools structure to support distribution in PyPI as 'cisco-dna-center'.

v.1.2.8.0: 31 Jan 2019
- Added a generic Crud class and wrapped it in DnacApi for use by all children instances
- Added CLI templates using Template and Deployment classes
- Created exceptions and applied them throughout
- Updated UML documentation
- Provided examples for NetworkDevice, CommandRunner and Template
- Updated module documentation

v.0.1: 21 Jan 2019
The initial contribution containing the base dnac module with its support for authentication and authorization when communicating with a Cisco DNA Center cluster, namely basicauth and xauthtoken.  In addition, five modules for performing API calls can be found:
- dnacapi - API base class
- networkdevice - handles network equipment managed by Cisco DNAC
- commandrunner - executes read-only commands on devices managed by Cisco DNAC
- task - monitors tasks running on Cisco DNAC
- taskresults - pulls the output created by completed tasks
