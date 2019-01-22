#
# dnac_config.py - configuration parameters for a Dnac object
#

'''
DNAC_NAME: FQDN of a DNAC cluster
           A Dnac instance prefers this value over an IP address (DNAC_IP)
           To use an IP address instead, set this constant = ""
'''
DNAC_NAME="denlab-en-dnac.cisco.com"

#
# DNAC_IP: IP address of a DNAC cluster
#
DNAC_IP="10.8.10.20"

#
# DNAC_VERSION: used for setting the resource path of API calls based upon
#               the version of the DNAC cluster.
#
DNAC_VERSION="1.2.8"

#
# DNAC_PORT: TCP port used to communicate with DNAC's API
#
DNAC_PORT="443"

#
# DNAC_USER: Name of a DNAC account with administrative privileges
#
DNAC_USER="admin"

#
# DNAC_PASSWD: Password for the DNAC_USER
#
DNAC_PASSWD="C!sco123"

#
# DNAC_CONTENT_TYPE: Data format with DNAC should respond with
#                    Valid values include: "application/json"
#                                          "application/xml"
#
DNAC_CONTENT_TYPE="application/json"

