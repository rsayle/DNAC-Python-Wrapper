from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ACCEPTED, \
                      REQUEST_NOT_ACCEPTED, \
                      ERROR_MSGS, \
                      _500_
from dnac.deployment import Deployment
from dnac.project import Project, \
                         PROJECT_RESOURCE_PATH, \
                         NO_TEMPLATES
from dnac.task import Task
import json
import time

MODULE = 'template.py'

TEMPLATE_RESOURCE_PATH = {
    '1.2.8': '/api/v1/template-programmer/template',
    '1.2.10': '/api/v2/template-programmer/template',
    '1.3.0.2': '/api/v2/template-programmer/template',
    '1.3.0.3': '/api/v2/template-programmer/template',
    '1.3.1.3': '/api/v2/template-programmer/template',
    '1.3.1.4': '/dna/intent/api/v1/template-programmer/template'
}

POST_1_2_8 = ['1.2.10', '1.3.0.2', '1.3.0.3', '1.3.1.3', '1.3.1.4']

TEMPLATE_VERSION_PATH = {
    '1.2.8': '/version',
    '1.2.10': '/version',
    '1.3.0.2': '/version',
    '1.3.0.3': '/version',
    '1.3.1.3': '/version',
    '1.3.1.4': '/version'
}

# monikers for importing templates
STUB_TEMPLATE = 'STUB_TEMPLATE'  # used as the name for an empty template when creating a new one
TEMPLATE_PARENT_KEY = 'parentTemplateId'  # used to test if a template is at least a parent or a versioned template
PARAM_SELECTION_KEY = 'selection'  # used to test if a parameter has a selection
PARAM_RANGE_KEY = 'range'  # used to test if a parameter has a range

# values instructing Cisco DNA Center how to interpret the target ID value
TARGET_BY_DEFAULT = 'DEFAULT'
TARGET_BY_ID = 'MANAGED_DEVICE_UUID'
TARGET_BY_HOSTNAME = 'MANAGED_DEVICE_HOSTNAME'
TARGET_BY_IP = 'MANAGED_DEVICE_IP'
TARGET_BY_SERIAL = 'PRE_PROVISIONED_SERIAL'
TARGET_BY_MAC = 'PRE_PROVISIONED_SERIAL'

VALID_TARGET_TYPES = [
    TARGET_BY_DEFAULT,
    TARGET_BY_ID,
    TARGET_BY_HOSTNAME,
    TARGET_BY_IP,
    TARGET_BY_SERIAL,
    TARGET_BY_MAC
]

# deployment states returned when checking on a deployment's status
DEPLOYMENT_INIT = 'INIT'
DEPLOYMENT_SUCCESS = 'SUCCESS'
DEPLOYMENT_FAILURE = 'FAILURE'

VALID_DEPLOYMENT_STATES = [
    DEPLOYMENT_INIT,
    DEPLOYMENT_SUCCESS,
    DEPLOYMENT_FAILURE
]

# end globals

# error conditions
TEMPLATE_ALREADY_DEPLOYED = 'already deployed with same params'
SUBSTR_NOT_FOUND = -1
TEMPLATE_IS_EMPTY = {}
NO_VERSIONS = {}

# error messages

TEMPLATE_NOT_FOUND = 'Could not find template'
NO_TEMPLATE_ID = 'The template ID is empty or does not exist'
NO_TEMPLATES_FOUND = 'Could not retrieve any templates'
INVALID_RESPONSE = 'Invalid response to API call'
EMPTY_TEMPLATE = 'Template has no data or does not exist'
EMPTY_TARGET = 'Template target ID is not set'
ILLEGAL_TARGET_TYPE = 'Illegal template target type'
UNKNOWN_DEPLOYMENT_STATUS = 'Unknown deployment status'
ALREADY_DEPLOYED = 'Template already deployed'
ILLEGAL_VERSION = 'Illegal template version'
LEGAL_VERSIONS = \
    'Template version must be 0 or greater. Use 0 to signal this API wrapper to use the latest version automatically.'
UNKNOWN_VERSION = 'Unknown template version'
ILLEGAL_NAME_CHANGE = 'Changing a template\'s name is prohibited'
ILLEGAL_NAME_CHANGE_RESOLUTION = 'Create a new Template object using a different template\'s name'
TEMPLATE_IMPORT_FAILED = 'Failed to import the template into DNA Center'
TEMPLATE_VERSION_FAILED = 'Failed to create a new version of the template'
TEMPLATE_CANNOT_BE_IMPORTED = 'Template cannot be imported into DNA Center'

# error resolutions
ALREADY_DEPLOYED_RESOLUTION = 'Change the template\'s parameters to a new value'
TEMPLATE_ALREADY_EXISTS = 'Template already exists'
TEMPLATE_CANNOT_BE_IMPORTED_RESOLUTION = 'Verify that the template is a parent or versioned template'
CALL_ADD_NEW_TEMPLATE = 'Use add_new_template before trying to add more versions to the Template'

# end error messages


class Template(DnacApi):
    """
    Class Template provides an abstraction of CLI templates in Cisco's DNA Center.  Once a network device has first
    been provisioned in Cisco DNAC, it's configuration can be updated with a CLI template. This class encapsulates the
    API calls and tools required to deploy a configuration template.

    A Template object's name must match the name it is given in a Cisco DNAC cluster.  You do not necessarily need to
    know in which project it is listed, but the name must be the same.  Be careful: template names in Cisco DNA Center
    are case sensitive.

    The power in using CLI templates is the ability to parameterize values that should be different across networking
    equipment.  For example, every router and switch could have a loopback interface for management, but they'll need
    to be assigned different IP addresses, naturally.  The Template class handles a template's parameters as a
    dictionary making it easy for programmers to update parameter values.

    Cisco DNA Center will not apply a template unless it is versioned.  In the Cisco DNA Center GUI, this amounts to
    having committed the template.  Stated differently, every template has a base instantiation in Cisco DNAC.  In the
    GUI, it's shown as the Local template and is the only one editable.  In the API, the base template is called the
    parent template and all versions reference the parent.  In the Template class, the parent template is referenced
    as version 0 and all other versions are referenced by their version number.

    Pushing a template causes Cisco DNA to create a deployment job. Depending upon the number of commands within a
    template as well as the list of target devices upon which to apply it, deployment jobs take a while to complete
    their tasks.  The Template class creates and holds a Deployment object for monitoring the job's status.  This
    happens automatically whenever the deploy() or deploy_sync() methods are called.

    Usage:
        d = Dnac()
        template = Template(d, 'Set VLAN')
        d.api['Set VLAN'].target_id = <switch_uuid>
        d.api['Set VLAN'].set_param('interface', 'gig1/0/1')
        d.api['Set VLAN'].set_param('vlan', 10)
        d.api['Set VLAN'].deploy_sync()
        pprint.PrettyPrint(template.deployment.results)
    """

    def __init__(self,
                 dnac,
                 name,
                 verify=False,
                 timeout=5):
        """
        Template's __init__ method constructs a new Template object. It automatically searches for the template in
        Cisco DNA Center by the Template's name.  If found, it will load the parent template information and all
        committed versions.  This class' attributes are decorator functions that directly access the template's info,
        the parent template, and all available versions.

        :param dnac: A reference to the master Dnac instance.
            type: Dnac object
            required: yes
            default: None
        :param name: The template's name as listed in Cisco DNA Center.
            type: str
            required: yes
            default: None
        :param verify: A flag that sets whether or not Cisco DNA Center's certificated should be authenticated.
            type: bool
            required: no
            default: False
        :param timeout: The number of seconds to wait for a response from Cisco DNAC.
            type: int
            required: no
            default: 5
        """
        # check Cisco DNA Center's version and set the resource path
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = TEMPLATE_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError('__init__: %s: %s' % (UNSUPPORTED_DNAC_VERSION, dnac.version))

        # template attributes
        self.__template = {}  # contents of the template info found by querying all available templates
        self.__versions = {}  # contents of the template's parent (index=0) and versionsInfo keyed by version number

        # deployment attributes
        self.__params = {}  # parameters and their values to apply during deployment
        self.__target_id = ''  # where to deploy the latest committed template
        self.__target_type = TARGET_BY_DEFAULT  # how to find the target
        self.__deployment = ''  # object for monitoring the deployment

        # DnacApi attributes
        super(Template, self).__init__(dnac,
                                       name,
                                       resource=path,
                                       verify=verify,
                                       timeout=timeout)

        # load the template
        if self.name != STUB_TEMPLATE:
            self.load_template(self.name)

    # end __init__()

    def __str__(self):
        """
        Returns a json formatted string of the template's base information.
        :return: str
        """
        return json.dumps(self.__template)

    # end __str__()

    def export_template(self):
        """
        Writes the base template information in json format to the file: <template_name>.tmpl
        :return: file
        """
        file = open('%s.tmpl' % self.__template['name'], mode='x')
        json.dump(self.__template, file, indent=4)
        file.close()

    # end export_template()

    def export_versioned_template(self, version=0):
        """
        Writes the versioned template given by the version parameter in json format to the file:
        <template_name>.<version>.tmpl
        :param version: The version to be exported to a file.  If no version is given, this method defaults to the
        parent template: version=0.
            type: int
            required: no
            default: 0
        :return: file
        """
        num_versions = len(self.__versions) - 1
        if version < 0 or version > num_versions:
            raise DnacApiError(
                MODULE, 'export_versioned_template', ILLEGAL_VERSION, '', LEGAL_VERSIONS, version, '', ''
            )
        target = self.__versions[version]
        file = open('%s.%i.tmpl' % (target['name'], version), mode='x')
        json.dump(target, file, indent=4)
        file.close()

    # end export_versioned_template()

    def __prepare_template__(self, template):
        """
        A hidden method that scrubs a template of all UUIDs and timestamps so that it can be safely imported into
        Cisco DNA Center.
        :param template: A reference to a template
            type: dict
            required: yes
            default: none
        :return: dict
        """
        # remove UUIDs and timestamps
        template.pop('id')
        template.pop('createTime')
        template.pop('lastUpdateTime')
        template.pop('parentTemplateId')
        # remove tags - future rev should rebuild tags
        template.pop('tags')
        # remove UUIDs from parameters list
        for param in template['templateParams']:
            param.pop('id')
            if PARAM_SELECTION_KEY in param.keys():
                param['selection'].pop('id')
            if PARAM_RANGE_KEY in param.keys():
                for range in param['range']:
                    range.pop('id')
        # return the prepared template
        return template

    # end __prepare_template__()

    def __prepare_version__(self, template, parent):
        """
        This hidden function first scrubs the template with __prepare_template__ and then modifies the template's
        id and parentTemplateId fields to point to the parent template so a new version can be committed.
        :param template: A reference to a template
            type: dict
            required: yes
            default: None
        :param parent: A reference to the parent template
            type: dict
            required: yes
            default: None
        :return: dict
        """
        # clean the template
        template = self.__prepare_template__(template)
        # set the parent template's UUID
        template['id'] = parent.template_id
        template['parentTemplateId'] = parent.template_id
        # return the prepared template
        return template

    # end __prepare_version__()

    def __is_versioned_template__(self, template):
        """
        A utility function to check that the template is formatted correctly for versioning.  If it is not, this
        method throws a DnacApiError; otherwise, it returns True.
        :param template: A reference to a template
            type: dict
            required: yes
            default: None
        :return: bool
        """
        # make sure this is a versioned template
        if TEMPLATE_PARENT_KEY not in template:
            raise DnacApiError(
                MODULE, 'import_template', TEMPLATE_CANNOT_BE_IMPORTED, '', '', '', '',
                '%s: %s: %s' % (TEMPLATE_CANNOT_BE_IMPORTED_RESOLUTION, template['name'], template['id'])
            )
        return True

    # end __is_versioned_template__()

    def add_new_template(self, template, project, timeout=5):
        """
        Creates a new template in Cisco DNA Center and assigns it to the project provided.
        :param template: The template information constructed from a json formatted string
            type: dict
            required: yes
            default: None
        :param project: A reference to the project to which the template should be assigned
            type: Project object
            required: yes
            default: None
        :return: Template object
        """
        # ensure the template is correctly formatted
        self.__is_versioned_template__(template)
        # prepare the template for import
        template = self.__prepare_template__(template)
        # add the template into DNA Center
        url = '%s%s/%s/template' % (self.dnac.url, PROJECT_RESOURCE_PATH[self.dnac.version], project.project_id)
        body = json.dumps(template)
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=body,
                                         verify=self.verify,
                                         timeout=timeout)
        if status != ACCEPTED:
            if status == _500_:
                raise DnacApiError(
                    MODULE, 'add_new_template', REQUEST_NOT_ACCEPTED, url,
                    ACCEPTED, status, ERROR_MSGS[status], TEMPLATE_ALREADY_EXISTS
                )
            else:
                raise DnacApiError(
                    MODULE, 'add_new_template', REQUEST_NOT_ACCEPTED, url, ACCEPTED, status, ERROR_MSGS[status], ''
                )
        # check the tasks' results
        task = Task(self.dnac, results['response']['taskId'])
        task.get_task_results()
        if task.is_error:
            raise DnacApiError(MODULE, 'add_new_template', TEMPLATE_IMPORT_FAILED, '', '', '', '', task.failure_reason)
        # import succeeded; reload the project and return the new template
        project.load_project(project.name)
        return Template(self.dnac, template['name'])

    # end add_new_template()

    def add_version(self, version, timeout=5):
        """
        Creates a new version of an existing template.
        :param version: The new version to be added to Cisco DNAC
            type: dict constructed from a json formatted file
            required: yes
            default: None
        :return: Template object
        """
        # ensure the template is correctly formatted
        self.__is_versioned_template__(version)
        # check if the template associated with the new version is already in Dnac
        if version['name'] not in self.dnac.api:
            # if not, throw an error
            raise DnacApiError(MODULE, 'add_version', '%s %s' % (TEMPLATE_NOT_FOUND, version['name']), '',
                               '', '', '', CALL_ADD_NEW_TEMPLATE)
        else:
            # if so, save a pointer to it
            template = self.dnac.api[version['name']]
        # prepare the new version
        self.__prepare_version__(version, template)
        # add the new version to DNAC
        url = '%s%s' % (self.dnac.url, TEMPLATE_RESOURCE_PATH[self.dnac.version])
        body = json.dumps(version)
        results, status = self.crud.put(url,
                                        headers=self.dnac.hdrs,
                                        body=body,
                                        verify=self.verify,
                                        timeout=timeout)
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, 'add_version', REQUEST_NOT_ACCEPTED, url, ACCEPTED, status, ERROR_MSGS[status], ''
            )
        # check the tasks' results
        task = Task(self.dnac, results['response']['taskId'])
        task.get_task_results()
        if task.is_error:
            raise DnacApiError(MODULE, 'add_version', TEMPLATE_IMPORT_FAILED, '', '', '', '', task.failure_reason)
        # import succeeded; reload the template
        return template.load_template(version['name'])

    # end add_version()

    def import_template(self, template_file, version_file):
        """
        The import_template method adds a template version to Cisco DNA Center.  It handles the work of determining
        if a new template is being created or if an existing template is being versioned.
        :param template_file: The file that contains the base template information (e.g. <template_name>.tmpl)
            type: str
            required: yes
            default: None
        :param version_file: The file that contains the versioned template (e.g. <template_name>.<version>.tmpl)
            type: str
            required: yes
            default: None
        :return: Template object
        """
        # read the template file's contents
        file = open(template_file, mode='r')
        template = json.load(file)
        file.close()

        # read the version file's contents
        file = open(version_file, mode='r')
        version = json.load(file)
        file.close()

        # load the template's project info; check Dnac first
        if template['projectName'] in self.dnac.api:
            project = self.dnac.api[template['projectName']]
        # not in Dnac so load it from DNAC
        else:
            # if the project does not exist, an exception will be thrown
            project = Project(self.dnac, template['projectName'])

        # check to see if the template is in the Project
        if project.templates == NO_TEMPLATES:
            # project has no templates; create a new one
            return self.add_new_template(version, project)
        else:
            # check the existing templates to see if the template exists or not
            for tmplt in project.templates:
                # if template exists, add a new version
                if tmplt['name'] == template['name']:
                    return self.add_version(version)
            # template does not exist; add a new template
            return self.add_new_template(version, project)

    # end import_template()

    def commit_template(self, comments='', timeout=5):
        """
        The commit_template updates the parent template to its next version.  Once completed, the actual template
        can be deployed in Cisco DNA Center.
        :param comments: Comments for the commit action
            type: str
            required: no
            default: ''
        :return: Template object
        """
        body = {
            'templateId': self.template_id,
            'comments': comments
        }
        url = '%s%s%s' % (self.dnac.url, self.resource, TEMPLATE_VERSION_PATH[self.dnac.version])
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=json.dumps(body),
                                         verify=self.verify,
                                         timeout=timeout)
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, 'version_template', REQUEST_NOT_ACCEPTED, url, ACCEPTED, status, ERROR_MSGS[status], ''
            )

        # check the tasks' results
        task = Task(self.dnac, results['response']['taskId'])
        task.get_task_results()
        if task.is_error:
            raise DnacApiError(MODULE, 'version_template', TEMPLATE_VERSION_FAILED, '', '', '', '', task.failure_reason)

        # version succeeded - reload the template and its versions
        return self.load_template(self.name)

    # end version_template

    @property
    def template(self):
        """
        Get method that returns the base template information.
        :return: dict
        """
        return self.__template

    # end template getter

    @property
    def template_id(self):
        """
        Get method that returns the base template's UUID.
        :return: str
        """
        return self.__template['templateId']

    # end template_id getter

    @property
    def parent(self):
        """
        Get method that returns the parent template's information.
        :return: dict
        """
        return self.__versions[0]

    # end parent getter

    @property
    def versions(self):
        """
        Get method for retrieving all of the template's versions.
        :return: list
        """
        return self.__versions

    # end versions getter

    @property
    def project_name(self):
        """
        Get method that provides the project to which the template is assigned.
        :return: str
        """
        return self.__template['projectName']

    # end project_name getter

    @property
    def project_id(self):
        """
        Get method that provides the project's UUID to which the template is assigned.
        :return: str
        """
        return self.__template['projectId']

    # end project_id getter

    @property
    def params(self):
        """
        Get method for retrieving the template's parameters.
        :return: list
        """
        return self.__params

    # end params getter

    @params.setter
    def params(self, params):
        """
        Set method for assigning a template's parameter list.
        :param params: The list of parameters and their values.
            type: list of dict
            required: yes
            default: None
        :return: None
        """
        self.__params = params

    # end params setter

    def set_param(self, key, value):
        """
        Adds a parameter and its value to the Template object's params dictionary.
        :param key: The parameter's name
            type: str
            required: yes
            default: None
        :param value: The parameter's value
            type: str
            required: yes
            default: None
        :return: None
        """
        self.__params[key] = value

    # end set_param()

    @property
    def target_id(self):
        """
        Template's target_id get method returns the UUID of the managed device where the template will be applied.
        :return: str
        """
        return self.__target_id

    # end target_id getter

    @target_id.setter
    def target_id(self, target_id):
        """
        Method target_id sets the value to the UUID of the network device where the template will be applied.
        :param target_id: The UUID of the device to which the template will be deployed.
            type: str
            required: yes
            default: None
        :return:
        """
        self.__target_id = target_id

    # end target_id setter

    @property
    def target_type(self):
        """
        Template's target_type get method returns the value used to instruct Cisco DNAC how to find targeted device in
        it inventory when applying a CLI template.
        :return: str: One of the following enumerated values:
                TARGET_BY_DEFAULT='DEFAULT'
                TARGET_BY_ID='MANAGED_DEVICE_UUID'
                TARGET_BY_HOSTNAME='MANAGED_DEVICE_HOSTNAME'
                TARGET_BY_IP='MANAGED_DEVICE_IP'
                TARGET_BY_SERIAL='PRE_PROVISIONED_SERIAL'
                TARGET_BY_MAC='PRE_PROVISIONED_SERIAL'
        """
        return self.__target_type

    # end target_type getter

    @target_type.setter
    def target_type(self, target_type):
        """
        Set method target_type changes the desired method that Cisco DNA Center uses to find a device in its inventory
        in order to apply the template.
        :param target_type: one of the following enumerated values:
                    TARGET_BY_DEFAULT='DEFAULT'
                    TARGET_BY_ID='MANAGED_DEVICE_UUID'
                    TARGET_BY_HOSTNAME='MANAGED_DEVICE_HOSTNAME'
                    TARGET_BY_IP='MANAGED_DEVICE_IP'
                    TARGET_BY_SERIAL='PRE_PROVISIONED_SERIAL'
                    TARGET_BY_MAC='PRE_PROVISIONED_SERIAL'
            type: str
            required: yes
            default: None
        :return: None
        """
        if target_type not in VALID_TARGET_TYPES:
            raise DnacApiError(
                MODULE, 'target_type setter', ILLEGAL_TARGET_TYPE, '', str(VALID_TARGET_TYPES), target_type, '', ''
            )
        self.__target_type = target_type

    # end target_type setter

    @property
    def deployment(self):
        """
        The deployment get method returns a reference to the Template's deploy job.  Use this attribute to monitor the
        job's status and get its results.
        :return: Deployment object
        """
        return self.__deployment

    # end deployment getter

    def get_all_templates(self):
        """
        Class method getAllTemplates queries the Cisco DNA Center cluster for a listing of every template it has.
        The listing includes the base templates and all of its versions.
        :return: list
        """
        filter = '?unCommitted=true'
        url = '%s%s%s' % (self.dnac.url, self.resource, filter)
        templates, status = self.crud.get(url,
                                          headers=self.dnac.hdrs,
                                          verify=self.verify,
                                          timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_all_templates', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], str(templates)
            )
        return templates

    # end get_all_templates()

    def get_template_by_id(self, id):
        """
        get_template_by_id pulls the template information from Cisco DNA Center specified by the UUID provided.
        Either base or versioned templates may be queried.
        :param id: The template's UUID
            type: str
            required: yes
            default: None
        :return: dict
        """
        url = self.dnac.url + self.resource + '/' + id
        template, status = self.crud.get(url,
                                         headers=self.dnac.hdrs,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_template_by_id', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], str(template)
            )
        return template

    # end get_template_by_id

    def get_versioned_template(self, version):
        """
        get_versioned_template searches the Template object's versions for the version requested and returns it.  Use
        version = 0 to retrieve the parent template.
        :param version: The desired template version
            type: int
            required: yes
            default: None
        :return: dict
        """
        if version not in self.__versions.keys():
            raise DnacApiError(
                MODULE, 'get_versioned_template', ILLEGAL_VERSION, '', '', version, '', ''
            )
        return self.__versions[version]

    # end get_versioned_template()

    def load_template(self, name):
        """
        The load_template method searches Cisco DNA Center for the template named.  If found, it loads the base
        template information and all available versions.  Use this function to prepare new Template objects or to
        refresh existing ones when they have changed.  Many methods in the Template class automatically call this
        function.  It should be rare for a user to have to call this method.
        :param name: The template's name as given in Cisco DNAC
            type: str
            required: yes
            default: None
        :return: Template object
        """
        # search all templates for the target
        templates = self.get_all_templates()
        if bool(templates):  # templates is not empty
            for template in templates:
                # find the template by name
                if template['name'] == name:
                    self.__template = template
                    break
                else:  # not found - keep looking for the template by its name
                    continue
            # make sure the template is not empty
            if self.__template == TEMPLATE_IS_EMPTY:
                raise DnacApiError(
                    MODULE, 'load_template', EMPTY_TEMPLATE, '', '', '', '', ''
                )
        else:
            raise DnacApiError(
                MODULE, 'load_template', NO_TEMPLATES_FOUND, '', '', '', '', ''
            )
        # load the parent template
        self.__versions[0] = self.get_template_by_id(self.__template['templateId'])
        # load all committed versions
        if bool(self.__template['versionsInfo']):  # at least one committed version exists
            for version in self.__template['versionsInfo']:
                self.__versions[int(version['version'])] = self.get_template_by_id(version['id'])
        # all done - return the template
        return self

    # end load_template()

    def __make_body__(self):
        """
        The __make_body__ method converts the Template object's target and versioned template information into a JSON
        encoded string used as the payload of a POST request to Cisco DNA Center.  Both deploy() and deploy_sync()
        automatically call this function.
        :return: json encoded str
        """
        tgt_info = {
            'type': self.__target_type,
            'id': self.__target_id,
            'params': self.__params
        }
        target_info = [tgt_info]
        if self.dnac.version == '1.2.8':
            body = {
                'template_id': self.parent['id'],
                'target_info': target_info
            }
        elif self.dnac.version in POST_1_2_8:
            body = {
                'templateId': self.parent['id'],
                'targetInfo': target_info
            }
        else:
            raise DnacApiError(
                MODULE, 'make_body', UNSUPPORTED_DNAC_VERSION, '',
                '', self.dnac.version, '', ''
            )
        return json.dumps(body)

    # end make_body()

    def deploy(self):
        """
        The deploy method asynchronously applies a template to a device. The Template's target information and
        versioned template data must be set prior to issuing this command.  The function creates a Deployment object,
        saves it, and then instructs it to perform a progress check on itself and then returns whatever Cisco DNA
        Center responds with.  Developers can then use the deployment instance to further monitor the job's success
        or failure.
        :return: str
        """
        url = self.dnac.url + self.resource + '/deploy'
        if not self.__target_id:  # target_id is not set
            raise DnacApiError(
                MODULE, 'deploy', EMPTY_TEMPLATE, url, '', self.__target_id, '', NO_TEMPLATE_ID
            )
        if self.__target_type not in VALID_TARGET_TYPES:
            raise DnacApiError(
                MODULE, 'deploy', ILLEGAL_TARGET_TYPE, url,
                str(VALID_TARGET_TYPES), self.__target_type, '',
                '%s is not one of %s' % (self.__target_type,
                                         str(VALID_TARGET_TYPES))
            )
        body = self.__make_body__()
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=body,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, 'check_deployment', REQUEST_NOT_ACCEPTED, url,
                ACCEPTED, status, ERROR_MSGS[status], str(results)
            )
        # DNAC 1.2.8 references a deploymentId in a string
        if self.dnac.version == '1.2.8':
            did = results['response']['deploymentId']
            elts = did.split()
            deploy_id = elts[len(elts) - 1]
        # DNAC 1.2.10 uses a task that references a deploymentId in a string
        elif self.dnac.version in POST_1_2_8:
            taskUrl = '%s%s' % (self.dnac.url, results['response']['url'])
            task, status = self.crud.get(taskUrl,
                                         headers=self.dnac.hdrs,
                                         verify=self.verify,
                                         timeout=self.timeout)
            progress = task['response']['progress']
            progress_elts = progress.split(': ')
            if progress_elts[3].find(TEMPLATE_ALREADY_DEPLOYED) != SUBSTR_NOT_FOUND:
                raise DnacApiError(
                    MODULE, 'deploy_sync', ALREADY_DEPLOYED, '', '', str(body), status, ALREADY_DEPLOYED_RESOLUTION
                )
            deploy_id = progress_elts[len(progress_elts) - 1]
        else:
            raise DnacApiError(
                MODULE, 'deploy', UNSUPPORTED_DNAC_VERSION, '',
                '', self.dnac.version, '', ''
            )
        self.__deployment = Deployment(self.dnac, deploy_id)
        return self.__deployment.check_deployment()

    # end deploy()

    def deploy_sync(self, wait=3):
        """
        deploy_sync pushes a template to the target device and then waits for the job to finish.  By default, it checks
        the job every three seconds, but this can be set using the wait keyword argument. The Template's target
        information and versioned template data must be set prior to issuing this command.  deploy_sync creates
        a deployment object, saves it, and uses it to monitor the job's progress.  Upon completion, deploy_sync returns
        the job's status.
        :param wait: The time to seconds to wait before checking the deployment job
            type: int
            required: no
            default: 3
        :return: str
        """
        url = self.dnac.url + self.resource + '/deploy'
        if not self.__target_id:  # target_id is not set
            raise DnacApiError(
                MODULE, 'deploy_sync', EMPTY_TEMPLATE, url, '', self.__target_id, '', NO_TEMPLATE_ID
            )
        if self.__target_type not in VALID_TARGET_TYPES:
            raise DnacApiError(
                MODULE, 'deploy_sync', ILLEGAL_TARGET_TYPE, url,
                str(VALID_TARGET_TYPES), self.__target_type, '',
                '%s is not one of %s' % (self.__target_type,
                                         str(VALID_TARGET_TYPES))
            )
        body = self.__make_body__()
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=body,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, 'deploy_sync', REQUEST_NOT_ACCEPTED, url, ACCEPTED, status, ERROR_MSGS[status], str(results)
            )
        # DNAC 1.2.8 references a deploymentId in a string
        if self.dnac.version == '1.2.8':
            did = results['response']['deploymentId']
            elts = did.split()
            deploy_id = elts[len(elts) - 1]
        # DNAC 1.2.10 uses a task that references a deploymentId in a string
        elif self.dnac.version in POST_1_2_8:
            taskUrl = '%s%s' % (self.dnac.url, results['response']['url'])
            task, status = self.crud.get(taskUrl,
                                         headers=self.dnac.hdrs,
                                         verify=self.verify,
                                         timeout=self.timeout)
            while 'endTime' not in task['response'].keys():
                time.sleep(wait)
                task, status = self.crud.get(taskUrl,
                                             headers=self.dnac.hdrs,
                                             verify=self.verify,
                                             timeout=self.timeout)
            progress = task['response']['progress']
            progress_elts = progress.split(': ')
            if progress_elts[3].find(TEMPLATE_ALREADY_DEPLOYED) != SUBSTR_NOT_FOUND:
                raise DnacApiError(
                    MODULE, 'deploy_sync', ALREADY_DEPLOYED, '', '', str(body), status, ALREADY_DEPLOYED_RESOLUTION
                )
            deploy_id = progress_elts[len(progress_elts) - 1]
        else:
            raise DnacApiError(
                MODULE, 'deploy_sync', UNSUPPORTED_DNAC_VERSION, '', '', self.dnac.version, '', ''
            )
        self.__deployment = Deployment(self.dnac, deploy_id)
        self.__deployment.check_deployment()
        while self.__deployment.status == DEPLOYMENT_INIT:
            time.sleep(wait)
            self.__deployment.check_deployment()
        return self.__deployment.status

    # end deploy_sync()

# end class Template()

