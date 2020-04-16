from dnac import Dnac
from dnac.project import Project, STUB_PROJECT
import sys

## Main program

# collect command line arguments
projects = sys.argv[1:]

# connect to the source Cisco DNA Center cluster
d = Dnac(name='',
         version='1.3.1.4',
         ip='10.91.33.113',
         port='443',
         user='admin',
         passwd='c!sco123',
         content_type='application/json')

# create a dummy Project object to perform the import
p = Project(d, STUB_PROJECT)

# for each project given on the command line
for project in projects:

    # import the project into DNAC
    new_project = p.import_project(project)

    if bool(new_project):
        print('Project %s imported.' % new_project.name)
