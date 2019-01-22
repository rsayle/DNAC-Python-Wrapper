# DNAC-Python-Wrapper
A python wrapper for easily accessing a Cisco DNA Center (DNAC) cluster.

# Purpose
The python modules herein simplify placing calls to Cisco's DNA Center.  They handle all the complexity involved with making CRUD calls to Cisco DNAC including:
  - Logging in and getting an XAuth token
  - Formatting URLs to control requests to Cisco DNAC
  - Parsing responses from Cisco DNAC and converting from json text into python objects

# Current State
v.0.1: 21 Jan 2019

The initial contribution containing the base dnac module with its support for authentication and authorization when communicating with a Cisco DNA Center cluster, namely basicauth and xauthtoken.  In addition, five modules for performing API calls can be found:
  1. dnacapi - API base class
  2. networkdevice - handles network equipment managed by Cisco DNAC
  3. commandrunner - executes read-only commands on devices managed by Cisco DNAC
  4. task - monitors tasks running on Cisco DNAC
  5. taskresults - pulls the output created by completed tasks

# Roadmap
- Configuration Templates
- Enancements to networkdevice
- Improving commandrunner's results

# License
This project is licensed by Cisco System's according to the terms stated in the project's file named [LICENSE](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/LICENSE).

# Modules
- dnac.py: Base Dnac class.
- dnac_config.py: Configuration file for instantiation a Dnac object.
- basicauth.py: HTTP basic authentication class, BasicAuth, used by Dnac objects.
- xauthtoken.py: X-auth-token class, XAuthToken, used by Dnac objects.
- dnacapi.py: DnacApi virtual class from which all API calls inherit.
- networkdevice.py: Manages devices in Cisco DNA Center.
- commandrunner.py: Runs read-only, i.e. show commands, on Cisco DNA Center.
- task.py: Manages tasks executing on Cisco DNAC.
- taskresults.py: Retrieves the output created by completed tasks.

# Documentation
Detailed documentation for each module, its classes, attributes and functions can be found in this project's HTML files or the docstrings contained within the modules themselves as well as in [Cisco DNA Center References](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-platform-overview/cisco-dna-center-platform-overview).

A summary diagram of the class hierarchy and their inter-relationships can be found in file [Cisco DNAC Wrapper UML](https://github.com/rsayle/DNAC-Python-Wrapper/blob/master/Cisco%20DNAC%20Wrapper%20UML.pdf).
