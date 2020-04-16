from dnac import Dnac
from dnac.project import Project
import sys

## Main program

# collect command line arguments
projects = sys.argv[1:]

# connect to the source Cisco DNA Center cluster
d = Dnac(name='denlab-en-dnac.cisco.com',
         version='1.3.1.3',
         ip='10.94.164.223',
         port='443',
         user='admin',
         passwd='C!sco123',
         content_type='application/json')

# for each project given on the command line
for project in projects:

    # load the project info
    p = Project(d, project)

    # save the project
    p.export_project()

    print("Exported project %s" % project)