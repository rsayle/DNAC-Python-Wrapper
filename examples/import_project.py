from dnac import Dnac
from dnac.project import Project, NEW_PROJECT
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

# create a dummy Project object to perform the import
p = Project(d, NEW_PROJECT)

# for each project given on the command line
for project in projects:

    # import the project into DNAC
    new_project = p.import_project(project)

    if bool(new_project):
        print('Project %s imported.' % new_project.name)
