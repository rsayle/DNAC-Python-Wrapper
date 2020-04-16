from dnac import Dnac
from dnac.template import Template
import sys

## Main program

# collect command line arguments
templates = sys.argv[1:]

# connect to the source Cisco DNA Center cluster
d = Dnac(name='denlab-en-dnac.cisco.com',
         version='1.3.1.3',
         ip='10.94.164.223',
         port='443',
         user='admin',
         passwd='C!sco123',
         content_type='application/json')

# for each template named on the command line
for template in templates:
    # get the template
    t = Template(d, template)

    # save the template
    t.export_template()

    # save all the template's versions
    for ver in t.versions:
        t.export_versioned_template(int(ver['version']))

    print('Exported template %s' % t.name)
