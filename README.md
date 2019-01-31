[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/rsayle/DNAC-Python-Wrapper)

# DNAC-Python-Wrapper
A python wrapper for easily accessing a Cisco DNA Center (DNAC) cluster.

# Purpose
The python modules herein simplify placing calls to Cisco's DNA Center.  They handle all the complexity involved with making CRUD calls to Cisco DNAC including:
  - Logging in and getting an XAuth token
  - Formatting URLs to control requests to Cisco DNAC
  - Parsing responses from Cisco DNAC and converting from json text into python objects

# License
This project is licensed by Cisco System's according to the terms stated in the project's file named [LICENSE](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/LICENSE).

# Modules
- [dnac.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/dnac.py): Base Dnac class.
- [dnac_config.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/dnac_config.py): Configuration file for instantiation a Dnac object.
- [basicauth.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/basicauth.py): HTTP basic authentication class, BasicAuth, used by Dnac objects.
- [xauthtoken.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/xauthtoken.py): X-auth-token class, XAuthToken, used by Dnac objects.
- [crud.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/crud.py): Crud class provides generic GET, PUT, POST and DELETE functions and is wrapped by DnacApi.
- [dnacapi.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/dnacapi.py): DnacApi virtual class from which all API calls inherit.
- [networkdevice.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/networkdevice.py): Manages devices in Cisco DNA Center.
- [networkdevice_example](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/networkdevice_example): An example script that shows how to use a NetworkDevice object.
- [commandrunner.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/commandrunner.py): Runs read-only, i.e. show commands, on Cisco DNA Center.
- [commandrunner_example](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/commandrunner_example): An example script showing how to use the CommandRunner class.
- [task.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/task.py): Manages tasks executing on Cisco DNAC.
- [taskresults.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/taskresults.py): Retrieves the output created by completed tasks.
- [template.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/template.py): Manages CLI templates.
- [template_example](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/template_example): An example script demonstrating how to use the Template class.
- [deployment.py](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/deployment.py): Monitors the progress of applying a CLI template to a network device.


# Documentation
Detailed documentation for each module, its classes, attributes and functions can be found in this project's HTML files or the docstrings contained within the modules themselves as well as in [Cisco DNA Center References](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-platform-overview/cisco-dna-center-platform-overview).

A summary diagram of the class hierarchy and their inter-relationships can be found in file [Cisco DNAC Wrapper UML](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/Cisco%20DNAC%20Wrapper%20UML.pdf).

# Current State
v.1.0: 31 Jan 2019

- Added a generic Crud class and wrapped it in DnacApi for use by all children instances
- Added CLI templates using Template and Deployment classes
- Created exceptions and applied them throughout
- Updated UML documentation
- Provided examples for NetworkDevice, CommandRunner and Template
- Updated module documentation

# Roadmap
- More enhancements to networkdevice
- Interface class
- Setting attributes as public, protected or private

# History
v.0.1: 21 Jan 2019

The initial contribution containing the base dnac module with its support for authentication and authorization when communicating with a Cisco DNA Center cluster, namely basicauth and xauthtoken.  In addition, five modules for performing API calls can be found:
  1. dnacapi - API base class
  2. networkdevice - handles network equipment managed by Cisco DNAC
  3. commandrunner - executes read-only commands on devices managed by Cisco DNAC
  4. task - monitors tasks running on Cisco DNAC
  5. taskresults - pulls the output created by completed tasks
