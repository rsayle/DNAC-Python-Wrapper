from dnac import Dnac
from dnac.template import Template, NEW_TEMPLATE
import sys

## Main program

# collect command line arguments
template = sys.argv[1]
versions = sys.argv[2:]

# connect to the source Cisco DNA Center cluster
d = Dnac(name='denlab-en-dnac.cisco.com',
         version='1.3.1.3',
         ip='10.94.164.223',
         port='443',
         user='admin',
         passwd='C!sco123',
         content_type='application/json')

# create a dummy Template object to perform the import
t = Template(d, NEW_TEMPLATE)

# for each template given on the command line
for version in versions:

    # import the template into DNAC
    new_template = t.import_template(template, version)

    # commit the new template so it becomes deployable
    new_template.commit_template(comments='Committed by import_template.py')

    if bool(new_template):
        print('Imported %s and created version from %s.' % (new_template.name, version))
