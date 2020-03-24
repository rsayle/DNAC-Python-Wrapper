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
In order to remain consistent with Cisco's DNA Center release cycle, this package follows DNAC's versioning.  In order for PyPi to treat this as the latest release, no more subversioning can be given; hence subversions will be listed in this readme.  The current subversion is 1.3.1.4.c.

# License
This project is licensed by Cisco Systems according to the terms stated in the project's [LICENSE](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.2.10.2/LICENSE) file.

# Modules
- [__init__.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/__init__.py): Contains the base Dnac class and controls the dnac package.
- [basicauth.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/basicauth.py): HTTP basic authentication class, BasicAuth, used by Dnac to perform a login.
- [client.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/client.py): Retrieves a client's state from Cisco DNAC for the time specified.
- [commandrunner.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/commandrunner.py): Runs read-only, i.e. show commands, on Cisco DNA Center.
- [commandrunner_task.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/commandrunner_task.py): Task handler for CommandRunner objects.
- [config_archive.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/config_archive.py): Manages Cisco DNA Center's configuration archive.
- [config_archive_settings.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/config_archive_settings.py): Manages Cisco DNA Center's configuration archive settings.
- [crud.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/crud.py): Crud class provides generic GET, PUT, POST and DELETE functions and is wrapped by DnacApi.
- [ctype.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/ctype.py): Stores the content type for API calls, e.g. application/json.
- [deployment.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/deployment.py): Monitors the progress of applying a CLI template to a network device.
- [device_archive.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/device_archive.py): Manages the configuration archive for a specific network device.
- [device_archive_task.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/device_archive_task.py): Manages the configuration archive tasks for a DeviceArchive object.
- [dnac_config.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/dnacapi.py): Configuration file for instantiating a Dnac object.
- [dnacapi.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/dnacapi.py): DnacApi virtual class from which all API calls inherit.
- [file.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/file.py): Retrieves the output created by completed tasks.
- [networkdevice.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/networkdevice.py): Manages devices in Cisco DNA Center, e.g. routers, switches, WLCs.
- [project.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/networkdevice.py): Retrieves a configuration template project.
- [site.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/site.py): A representation of a site's attributes and state.
- [site_hierarchy.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/site_hierarchy.py): Builds a representation of the sites in Cisco DNA Center's Network Hierarchy.
- [task.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/task.py): Manages tasks executing on Cisco DNAC.
- [template.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/template.py): Manages CLI templates.
- [timestamp.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/timestamp.py): Converts the system's time in UTC into milliseconds for pulling client and site state information from Cisco DNA Center.
- [version.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/version.py): A representation of a specific version of a network device's archive.
- [xauthtoken.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/dnac/xauthtoken.py): X-auth-token class, XAuthToken, used by Dnac to authorize commands after a successful login.


# Examples
- [commandrunner_example.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/examples/commandrunner_example.py): An example script showing how to use the CommandRunner class.
- [config_archive.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/examples/config_archiver.py): An HTTP server for managing device archives.
- [export_project.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/examples/export_project.py): Exports a configuration template project to a file.
- [export_template.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/examples/export_template.py): Exports a configuration template and all its versions to files.
- [import_project.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/examples/import_project.py): Imports a configuration template project from a file.
- [import_template.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/examples/import_template.py): Imports a configuration template and all its versions from files.
- [networkdevice_example.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/examples/networkdevice_example.py): An example script that shows how to use a NetworkDevice object.
- [network_hierarchy_replicator](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/examples/network_hierarchy_replicator.py): An HTTP server for replicating sites in the network design hierarchy from one cluster to another.
- [template_example.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/examples/template_example.py): An example script demonstrating how to use the Template class.
- [template_replicator.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/examples/template_replicator.py): An HTTP server for replicating configuration templates and projects.

# Documentation
Detailed documentation for each module, its classes, attributes and functions can be found in [this project's HTML files](https://github.com/rsayle/DNAC-Python-Wrapper/tree/1.3.1.4/docs) or the docstrings contained within the modules themselves as well as in [Cisco DNA Center References](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-platform-overview/cisco-dna-center-platform-overview).

A summary diagram of the class hierarchy and their inter-relationships can be found in file [Cisco DNAC Wrapper UML](https://github.com/rsayle/DNAC-Python-Wrapper/blob/1.3.1.4/docs/Cisco%20DNAC%20Wrapper%20UML.pdf).

# Current State
v.1.3.1.4.c: 23 Mar 2020
- Converted all modules to docstring format
- Enhanced Site class
- Added SiteHeirarchy and SiteNode classes in new module: site_hierarchy.py
- Added network_design_hierarchy example
- Updated UML documentation
- Removed all unit testing from each module

# Roadmap
- Move unit test code from being embedded in modules to a test package structure.
- More enhancements to networkdevice
- Interface class
- Remove support for Cisco DNA Center 1.2.8.

# History
v.1.3.1.4.b: 7 Mar 2020
- Overhauled Task and Deployment classes
- Fixed bugs in Template class

v.1.3.1.4.a: 17 Jan 2020
- Overhauled Template class and added methods to export, import and commit templates
- New modules for managing device configuration archives: config_archive, config_archive_settings, device_archive, device_archive_task
- New example for managing device configuration archives: config_archiver
- New example for exporting/importing configuration templates and projects: export_project, export_template, import_project, import_template
- Began adopting standard doc string formats

v.1.2.10.3: 2 Jun 2019
- Fixed defect in networkdevice module

v.1.2.10.2: 24 May 2019
- Added client, site, and timestamp classes
- Fixed various defects
- Adjusted template class to handle behavior changes from 1.2.8 to 1.2.10

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
