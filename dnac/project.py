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
    '1.3.1.3': '/api/v2/template-programmer/project',
    '1.3.1.4': '/api/v2/template-programmer/project'
}

# globals

STUB_PROJECT = 'STUB_PROJECT'

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
    """
    The Project class represents a configuration template project in Cisco DNA Center.  It serves as a container for
    grouping templates.  Templates must be associated with a project.  If a template cannot be associated to an
    existing project, create the project first.

    Usage:
        d = Dnac()
        proj = Project(d, 'aProject')
        pprint.PrettyPrinter(proj.project)
    """

    def __init__(self,
                 dnac,
                 name,
                 verify=False,
                 timeout=5):
        """
        Upon creating a new Project object, __init__ sets the __project field as an empty dict.  As long as the
        project's name is not set to 'NEW_PROJECT', the Project attempts to load its attributes as given in Cisco
        DNA Center.  If its name is NEW_PROJECT, then this method creates an empty Project that can be used to
        import a project from a backup file (see the import_project method for more details).
        Usage:
            d = Dnac()
            proj = Project(d, 'aProject')
        :param dnac: a reference to the containing Dnac object
            type: Dnac object
            default: none
            required: yes
        :param name: the project's name as it appears in a live Cisco DNA Center cluster
            type: str
            default: none
            required: yes
        :param verify: a flag used to check DNAC's certificate
            type: bool
            default: False
            required: no
        :param timeout: the time in seconds to wait for an API response from DNA Center
            type: int
            default: 5
            required: no
        """
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
        if self.name != STUB_PROJECT:
            self.load_project(self.name)

    # end __init__()

    def __str__(self):
        """
        Returns the Project's contents as a json formatted string.
        :return: str
        """
        return json.dumps(self.__project)

    # end __str__()

    @property
    def project(self):
        """
        Get method for the object's project field, which contains the project's complete representation as given in
        Cisco DNAC.
        :return: dict
        """
        return self.__project

    # end project getter

    @property
    def description(self):
        """
        Provides the project's description.
        :return: str
        """
        return self.__project['description']

    # end description getter

    @property
    def templates(self):
        """
        Lists the templates contained in the project.
        :return: list
        """
        return self.__project['templates']

    # end templates getter

    @property
    def project_id(self):
        """
        Furnishes the project's UUID.
        :return: str
        """
        return self.__project['id']

    # end project_id getter

    @property
    def project_name(self):
        """
        Gives the project's name.
        :return: str
        """
        return self.__project['name']

    # end project_name getter

    @property
    def tags(self):
        """
        Lists all tags associated to the project.
        :return: list
        """
        return self.__project['tags']

    # end tags getter

    @property
    def is_deletable(self):
        """
        Defines whether or not the project can be deleted.
        :return: bool
        """
        return self.__project['isDeletable']

    # end is_deletable getter

    def export_project(self):
        """
        Writes the project as a json formatted string to a file.  The file will be named according to the format:
            <Project.name>.proj
        :return: file
        """
        file = open('%s.proj' % self.__project['name'], mode='x')
        json.dump(self.__project, file, indent=4)
        file.close()

    # end export_project

    def __clean_project__(self, project):
        project.pop('id')
        project.pop('templates')
        return project

    # end __clean_project__()

    def add_project(self, project):
        """
        Adds a project to Cisco DNA Center
        :param project: The project data represented as a dict
        :return: Project object
        """
        # add the project to Cisco DNA Center
        url = '%s%s' % (self.dnac.url, self.resource)
        self.__clean_project__(project)
        body = json.dumps(project)
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
        return Project(self.dnac, project['name'])

    # end add_project()

    def import_project(self, project):
        """
        Creates a new project from a file.
        :param project: File name containing the project's parameters
        :return: Project object
        """
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
        return self.add_project(data)

    # end import_project

    def load_project(self, name):
        """
        Loads a project's attributes from Cisco DNA Center.  This method can be used to refresh a Project object's
        fields when API calls have been made that modify the project.
        :param name: The project's name in Cisco DNAC
        :return: Project object
        """
        # load the project by name
        self.get_project_by_name(name)
        if self.__project == NO_PROJECT:
            raise DnacApiError(
                MODULE, 'load_project', PROJECT_NOT_FOUND, '',
                name, str(self.__project), '', CHECK_OR_CREATE_PROJECT
            )
        # load all templates associated with the project
        return self

    # end load_project()

    def get_all_projects(self):
        """
        The get_all_projects method returns all projects residing in Cisco DNAC.
        :return: list
        """
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
        """
        Get_project_by_name queries Cisco DNA Center to return the project specified in the name parameter.  If found,
        the method loads the project's details in the object's __project dictionary.
        :param name: Project name to search for
        :return: Project object
        """
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
