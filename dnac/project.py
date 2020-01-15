from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ACCEPTED, \
                      REQUEST_NOT_ACCEPTED, \
                      ERROR_MSGS
from dnac.task import Task
import json

MODULE = 'project.py'

PROJECT_RESOURCE_PATH = {
    '1.3.1.3': '/api/v2/template-programmer/project'
}

# globals

NEW_PROJECT = 'NEW_PROJECT'

# error conditions
NO_PROJECT = [[], {}]
NO_TEMPLATES = []

# error messages
PROJECT_NOT_FOUND = 'Could not find the project named'
PROJECT_ALREADY_EXISTS = 'Project already exists'
PROJECT_IMPORT_FAILED = 'Failed to import the project'
ILLEGAL_PROJECT_LIST = 'Multiple projects were returned when searching by name'

# error resolutions
CHECK_OR_CREATE_PROJECT = 'Check the project\'s name in DNA Center or create it if it does not exist'
USE_UNIQUE_PROJECT_NAME = 'Choose a project name that does not exist in DNA Center'

class Project(DnacApi):

    def __init__(self,
                 dnac,
                 name,
                 verify=False,
                 timeout=5):

        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = PROJECT_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError('%s: __init__: %s: %s' % (MODULE, UNSUPPORTED_DNAC_VERSION, dnac.version))

        # initialize attributes
        self.__project = {}

        # setup the parent class
        super(Project, self).__init__(dnac,
                                      name,
                                      resource=path,
                                      verify=verify,
                                      timeout=timeout)

        # retrieve the project
        if self.name != NEW_PROJECT:
            self.load_project(self.name)

    # end __init__()

    @property
    def description(self):
        return self.__project['description']

    # end description getter

    @property
    def templates(self):
        return self.__project['templates']

    # end templates getter

    @property
    def project_id(self):
        return self.__project['id']

    # end project_id getter

    @property
    def project_name(self):
        return self.__project['name']

    # end project_name getter

    @property
    def tags(self):
        return self.__project['tags']

    # end tags getter

    @property
    def is_deletable(self):
        return self.__project['isDeletable']

    # end is_deletable getter

    def export_project(self):
        file = open('%s.proj' % self.__project['name'], mode='x')
        json.dump(self.__project, file, indent=4)
        file.close()

    # end export_project

    def import_project(self, project):
        # get the project data from the file named
        file = open(project, mode='r')
        data = json.load(file)
        file.close()
        # check that the project to be imported is unique
        self.get_project_by_name(data['name'])
        if self.__project not in NO_PROJECT:
            raise DnacApiError(
                MODULE, 'import_project', PROJECT_ALREADY_EXISTS, '', '', data['name'], '', USE_UNIQUE_PROJECT_NAME
            )
        # import the project into Cisco DNA Center
        url = '%s%s' % (self.dnac.url, self.resource)
        body = json.dumps(data)
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=body,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, 'import_project', REQUEST_NOT_ACCEPTED, url, ACCEPTED, status, ERROR_MSGS[status], ''
            )
        # check the tasks' results
        task = Task(self.dnac, results['response']['taskId'])
        task.get_task_results()
        if task.is_error:
            raise DnacApiError(MODULE, 'import_project', PROJECT_IMPORT_FAILED, '', '', '', '', task.failure_reason)
        # import succeeded; create a new Project object, add it to Dnac and return it
        return Project(self.dnac, data['name'])

    # end import_project

    def load_project(self, name):
        # load the project by name
        self.get_project_by_name(name)
        if self.__project == NO_PROJECT:
            raise DnacApiError(
                MODULE, 'load_project', PROJECT_NOT_FOUND, '',
                name, str(self.__project), '', CHECK_OR_CREATE_PROJECT
            )
        return self

    # end load_project()

    def get_all_projects(self):
        url = self.dnac.url + self.resource
        projects, status = self.crud.get(url,
                                         headers=self.dnac.hdrs,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != OK:
            raise DnacApiError(MODULE, 'get_all_projects', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], '')
        return projects

    # end get_all_projects

    def get_project_by_name(self, name):
        filter = '?name=%s' % name
        url = '%s%s%s' % (self.dnac.url, self.resource, filter)
        project, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(MODULE, 'get_project_by_name', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], name)
        if project not in NO_PROJECT:
            if len(project) > 1 or len(project) <= 0:
                raise DnacApiError(
                    MODULE, 'get_project_by_name', ILLEGAL_PROJECT_LIST, '', '1', str(len(self.__project)), '', ''
                )
            self.__project = project[0]
        return self

# end class Project
