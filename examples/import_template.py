from dnac import Dnac
from dnac.template import Template, STUB_TEMPLATE
import sys

## Main program

# collect command line arguments
template = sys.argv[1]
versions = sys.argv[2:]

# connect to the source Cisco DNA Center cluster
d = Dnac(name='',
         version='1.3.1.4',
         ip='10.91.33.113',
         port='443',
         user='admin',
         passwd='c!sco123',
         content_type='application/json')

# create a dummy Template object to perform the import
t = Template(d, STUB_TEMPLATE)

# for each template given on the command line
for version in versions:

    # import the template into DNAC
    new_template = t.import_template(template, version)

    # commit the new template so it becomes deployable
    new_template.commit_template(comments='Committed by import_template.py')

    if bool(new_template):
        print('Imported %s and created version from %s.' % (new_template.name, version))
