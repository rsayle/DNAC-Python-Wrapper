
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
from dnac.deployment import Deployment
import json
import time

MODULE = 'template.py'

TEMPLATE_RESOURCE_PATH = {
    '1.2.8': '/api/v1/template-programmer/template',
    '1.2.10': '/api/v2/template-programmer/template'
}

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

# error resolutions
ALREADY_DEPLOYED_RESOLUTION = 'Change the template\'s parameters to a new value'

# end error messages


class Template(DnacApi):
    """
    Class Template provides an abstraction of CLI templates in Cisco's
    DNA Center.  Once a network device has first been provisioned in
    Cisco DNAC, it's configuration can be updated with a CLI template.
    This class encapsulates the API calls and tools required to deploy
    a configuration template.

    A Template object's name must match the name it is given in a Cisco
    DNAC cluster.  You do not necessarily need to know in which project
    it is listed, but the name must be the same.  Be careful: template
    names in Cisco DNA Center are case sensitive.

    The power in using CLI templates is the ability to parameterize values
    that should be different across networking equipment.  For example,
    every router and switch could have a loopback interface for management,
    but they'll need to be assigned different IP addresses, naturally.  The
    Template class handles a template's parameters as a dictionary making
    it easy for programmers to update parameter values.

    Cisco DNA Center will not apply a template unless it is versioned.  In
    the Cisco DNA Center GUI, this amounts to having committed the
    template.  Stated differently, every template has a base instantiation
    in Cisco DNAC, but the base template cannot be deployed.  Instead,
    users must access a committed version of the template.  The Template
    class stores the base template in its template attribute and then
    allows the selection of a particular version of the template using
    its version attribute.  To use the latest version, simply set version's
    value to zero, which is the default setting.

    Pushing a template causes Cisco DNA to create a deployment job.
    Depending upon the number of commands within a template as well as the
    list of target devices upon which to apply it, deployment jobs take
    a while to complete their tasks.  The Template class creates and holds
    a Deployment object for monitoring the job's status.  This happens
    automatically whenever the deploy() or deploy_sync() methods are called.

    Attributes:
        dnac:
            Dnac object: A reference to the Dnac instance that contains
                         the Template object
            default: none
            scope: protected
        name:
            str: A user friendly name for the Template object that is
                 used both as a key for finding it in a Dnac.api attribute
                 and for locating the real CLI template in Cisco DNAC.
                 The template name must match its name in Cisco DNAC
                 exactly including its case.
            default: none
            scope: protected
        version:
            int: The version of a template to be deployed.  Setting the
                 version to zero signals the Template object to use
                 whatever the latest version may be.

                 Changing a Template's version causes the object to
                 search for and load the requested versioned template
                 according to the Template's name.  If the requested
                 version does not exist, Template throws an exception.

                 When switching to a different template in Cisco DNA
                 Center either create a new Template object altogether
                 or first change the Template's name, which will trigger
                 the object to load the latest version, and then update
                 the version attribute so that the Template instance
                 loads the correct one.
            default: 0
            scope: public
        template_id:
            str: The UUID in Cisco DNAC of the base template.  A base
                 template cannot be deployed on any equipment.
            default: none
            scope: protected
        versioned_template:
            dict: The CLI template as represented in Cisco DNA Center.
            default: none
            scope: protected
        versioned_template_id:
            str: The UUID in Cisco DNAC of committed template, which can
                 be deployed.
            default: none
            scope: protected
        versioned_template_params:
            dict: A dictionary whose keys are the template's parameter
                  names.  Their values can each be set directly through
                  accessing this dictionary.  See the example below in
                  the Usage section.
            default: none
            scope: protected
        target_id:
            str: The UUID of a network device to which the template
                 will be applied.
            default: none
            scope: public
        target_type:
            str: An enumerated value that instructs Cisco DNA Center how
                 to find the device so that the template can be applied.
                 Legal values for target_type are kept in the global
                 list:
                    VALID_TARGET_TYPES=[TARGET_BY_DEFAULT,
                                        TARGET_BY_ID,
                                        TARGET_BY_HOSTNAME,
                                        TARGET_BY_IP,
                                        TARGET_BY_SERIAL,
                                        TARGET_BY_MAC]
            default: TARGET_BY_DEFAULT
            scope: public
        deployment:
            Deployment object: A Deployment instance that provides the
                               deploy job's status and the job's results.
            default: none
            scope: protected
    Usage:
        d = Dnac()
        template = Template(d, 'Set VLAN')
        d.api['Set VLAN'].target_id = <switch_uuid>
        d.api['Set VLAN'].versioned_template_params['interface'] = 'gig1/0/1'
        d.api['Set VLAN'].versioned_template_params['vlan'] = 10
        d.api['Set VLAN'].deploy_sync()
        pprint.PrettyPrint(template.deployment.results)
    """

    def __init__(self,
                 dnac,
                 name,
                 version=0,
                 verify=False,
                 timeout=5):
        """
        Template's __init__ method constructs a new Template object.
        It automatically searches for the template in Cisco DNA Center
        by the Template's name.  If found, then it will search for the
        committed version of the template according to the value passed
        in the version keyword argument.  If no version is selected, it
        chooses the latest version available.

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: none
                required: yes
            name: The template's exact name, including its case, in
                  Cisco DNA Center.
                type: str
                default: none
                required: yes
            version: The template version that will be deployed.  When set
                     to zero, Template selects the latest version.
                type: int
                default: 0
                required: no
            verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: no
            timeout: The number of seconds to wait for Cisco DNAC's
                     response.
                type: int
                default: 5
                required: no

        Return Values:
            Template object: a newly build Template instance.

        Usage:
            d = Dnac()
            template = Template(d, 'Enable BGP', version=5)
        """
        # version is the template's version and must not be negative
        if version < 0:
            raise DnacApiError(
                MODULE, '__init__', ILLEGAL_VERSION, '', '',
                version, '', LEGAL_VERSIONS
            )
        # check Cisco DNA Center's version and set the resource path
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = TEMPLATE_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError(
                '__init__: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
            )
        # setup initial attribute values
        self.__template_id = ''  # base template ID
        self.__version = version  # requested template version, 0 = latest
        self.__versioned_template = {}
        self.__versioned_template_id = ''  # template that can be deployed
        self.__versioned_template_params = {}
        self.__target_id = ''  # where to deploy the template
        self.__target_type = TARGET_BY_DEFAULT  # how to find the target
        self.__deployment = ''  # object for monitoring the deployment
        super(Template, self).__init__(dnac,
                                       name,
                                       resource=path,
                                       verify=verify,
                                       timeout=timeout)
        # retrieve the template ID by its name
        self.__template_id = self.get_template_by_name(self.name)
        if not self.__template_id:  # template could not be found
            raise DnacApiError(
                MODULE, '__init__', TEMPLATE_NOT_FOUND, '',
                '', self.__template_id, '', ''
            )
        # retrieve the versioned template
        # get_versioned_template_by_name sets self.__versioned_template
        self.get_versioned_template_by_name(self.name, self.__version)
        if not bool(self.__versioned_template):  # template is empty
            # get_versioned_template_by_name should catch this condition, but
            # just in case, here's another integrity check
            raise DnacApiError(
                MODULE, '__init__', UNKNOWN_VERSION, '',
                '', self.__versioned_template, '',
                '%s version %i' % (self.name, self.__version)
            )

    # end __init__()

    @property
    def template_id(self):
        """
        Get method template_id returns the base template's UUID from Cisco
        DNA Center.

        Parameters:
            none

        Return Values:
            str: The template's UUID.

        Usage:
            d = Dnac()
            template = Template(d, 'Add Loopback')
            print (d.api['Add Loopback'].template_id)
        """
        return self.__template_id

    # end template_id getter

    @property
    def version(self):
        """
        The version get method returns the template's version number.

        Parameters:
            none

        Return Value:
            int: The template's version number.

        Usage:
            d = Dnac()
            template = Template(d, 'Add Loopback')
            print d.api['Add Loopback'].version
        """
        return self.__version

    # end version getter

    @version.setter
    def version(self, version):
        """
        The version set method changes the desired version of the template
        to be deployed.  This method also updates the versioned template,
        its UUID and its parameters in this class' respective attributes.
        See class method get_versioned_template_by_name for details.  If the
        requested version does not exist, an exception is thrown.

        Parameters:
            version: The new template version.
                type: int
                default: none
                required: yes

        Return Values:
            none

        Usage:
            d = Dnac()
            template = Template(d, 'Set VLAN')
            template.version = 5
        """
        self.__version = version
        # reload versioned template info using get_versioned_template_by_name
        self.get_versioned_template_by_name(self.name, self.__version)
        # if the version requested does not exist, raise an exception
        if not bool(self.__versioned_template):  # template is empty
            # get_versioned_template_by_name should catch this condition, but
            # just in case, here's another integrity check
            raise DnacApiError(
                MODULE, 'version setter', UNKNOWN_VERSION, '',
                '', self.__versioned_template, '',
                '%s version %i' % (self.name, version)
            )

    # end version setter

    @property
    def versioned_template(self):
        """
        The versioned_template get method returns the template's contents.

        Parameters:
            none

        Return Value:
            dict: The template's data.

        Usage:
            d = Dnac()
            template = Template(d, 'Add Loopback')
            print str(d.api['Add Loopback'].versioned_template)
        """
        return self.__versioned_template

    # end versioned_template getter

    @property
    def versioned_template_id(self):
        """
        The versioned_template_id get method returns the UUID for the
        committed template based upon the object's current template version.

        Parameters:
            none

        Return Value:
            str: The versioned template's UUID in Cisco DNA Center

        Usage:
            d = Dnac()
            template = Template(d, 'Add Loopback')
            print d.api['Add Loopback'].versioned_template_id
        """
        return self.__versioned_template_id

    # end versioned_template_id getter

    @property
    def versioned_template_params(self):
        """
        versioned_template_params returns the template's parameters
        dictionary.  Values may be updated directly by accessing this
        attribute.

        Parameters:
            none

        Return Value:
            dict: The template's parameters and their current values.

        Usage:
            d = Dnac()
            template = Template(d, 'Add Loopback')
            print str(d.api['Add Loopback'].versioned_template_params)
            d.api['Add Loopback'].versioned_template_params['ip'] = 10.1.1.1
        """
        return self.__versioned_template_params

    # end versioned_template_params getter

    @property
    def target_id(self):
        """
        Template's target_id get method returns the UUID of the managed
        device where the template will be applied.

        Parameters:
            none

        Return Values:
            str: A Cisco DNAC managed device's UUID.

        Usage:
            d = Dnac()
            template = Template(d, 'Add Loopback')
            print d.api['Add Loopback'].target_id
        """
        return self.__target_id

    # end target_id getter

    @target_id.setter
    def target_id(self, target_id):
        """
        Method target_id sets the value to the UUID of the network device
        where the template will be applied.

        Parameters:
            target_id:
                type: str
                default: none
                required: yes

        Return Values:
            None

        Usage:
            d = Dnac()
            template = Template(d, 'Enable EIGRP')
            d.api['Enable EIGRP'].target_id = '<router_UUID>'
        """
        self.__target_id = target_id

    # end target_id setter

    @property
    def target_type(self):
        """
        Template's target_type get method returns the value used to instruct
        Cisco DNAC how to find targeted device in it inventory when
        applying a CLI template.

        Parameters:
            none

        Return Values:
            str: One of the following enumerated values:
                TARGET_BY_DEFAULT='DEFAULT'
                TARGET_BY_ID='MANAGED_DEVICE_UUID'
                TARGET_BY_HOSTNAME='MANAGED_DEVICE_HOSTNAME'
                TARGET_BY_IP='MANAGED_DEVICE_IP'
                TARGET_BY_SERIAL='PRE_PROVISIONED_SERIAL'
                TARGET_BY_MAC='PRE_PROVISIONED_SERIAL'

        Usage:
            d = Dnac()
            template = Template(d, 'Set VLAN')
            print d.api['Set VLAN'].target_type
        """
        return self.__target_type

    # end target_type getter

    @target_type.setter
    def target_type(self, target_type):
        """
        Set method target_type changes the desired method that Cisco DNA
        Center uses to find a device in its inventory in order to apply
        the template.

        Paramters:
            target_type:
                str: one of the following enumerated values:
                    TARGET_BY_DEFAULT='DEFAULT'
                    TARGET_BY_ID='MANAGED_DEVICE_UUID'
                    TARGET_BY_HOSTNAME='MANAGED_DEVICE_HOSTNAME'
                    TARGET_BY_IP='MANAGED_DEVICE_IP'
                    TARGET_BY_SERIAL='PRE_PROVISIONED_SERIAL'
                    TARGET_BY_MAC='PRE_PROVISIONED_SERIAL'
                default: none
                required: yes

        Return Values:
            none

        Usage:
            d = Dnac()
            template = Template(d, 'Set VLAN')
            d.api['Set VLAN'].target_type = TARGET_BY_HOSTNAME
        """
        self.__target_type = target_type

    # end target_type setter

    @property
    def deployment(self):
        """
        The deployment get method returns a reference to the Template's
        deploy job.  Use this attribute to monitor the job's status and
        get its results.

        Parameters:
            none

        Return Values:
            Deployment object: The job for the deployed template.

        Usage:
            d = Dnac()
            template = Template(d, 'Set VLAN')
            print str(d.api['Set Vlan'].deployment.results)
        """
        return self.__deployment

    # end deployment getter

    def get_all_templates(self):
        """
        Class method getAllTemplates queries the Cisco DNA Center cluster
        for a listing of every template it has.  The listing includes
        the base templates and all of its versions.

        Parameters:
            none

        Return Values:
            list: A listing of all available templates.

        Usage:
            d = Dnac()
            template = Template(d, 'Set VLAN')
            print str(d.api['Set Vlan'].getAllTemplates)
        """
        url = self.dnac.url + self.resource
        templates, status = self.crud.get(url,
                                          headers=self.dnac.hdrs,
                                          verify=self.verify,
                                          timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_all_templates', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(templates)
            )
        return templates

    # end get_all_templates()

    def get_template_by_id(self, id):
        """
        get_template_by_id pulls the template information for the one
        specified by the UUID passed to the function.  Either base or
        versioned templates may be queried.

        Parameters:
            id: The UUID of a template.
                type: str
                default: none
                required: yes

        Return Values:
            dict: The template's data.

        Usage:
            d = Dnac()
            template = Template(d, 'Set VLAN')
            print str(d.api['Set Vlan'].get_template_by_id('<template_uuid>')
        """
        url = self.dnac.url + self.resource + '/' + id
        template, status = self.crud.get(url,
                                         headers=self.dnac.hdrs,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_template_by_id', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(template)
            )
        return template

    # end get_template_by_id

    def get_template_by_name(self, name):
        """
        get_template_by_name finds the base template by its name and
        saves the value in its __template_id attribute and returns it.

        Parameters:
            name: The template's name, which must match exactly as it
                  is entered in Cisco DNA Center.  If no name is given,
                  the method defaults to the Template object's own name.
                type: str
                default: none
                required: no

        Return Values:
            str: The template's UUID.

        Usage:
            d = Dnac()
            template = Template(d, 'Set VLAN')
            print str(d.api['Set Vlan'].getTemplateByIdByName()
        """
        if not name:  # parameter name was not given a value
            name = self.__name  # use the Template's name
        self.__template_id = ''
        # find the template by name
        templates = self.get_all_templates()
        if bool(templates):  # templates is not empty
            for template in templates:
                # find the template by name, save it and save its ID
                if template['name'] == name:
                    self.__template_id = template['templateId']
                else:  # keep looking for the template by its name
                    continue
        else:
            raise DnacApiError(
                MODULE, 'get_template_by_name', NO_TEMPLATES_FOUND, '',
                '', '', '', ''
            )
        # all done - return the template's UUID
        return self.__template_id

    # end get_template_by_name()

    def get_versioned_template_by_name(self, name, ver=0):
        """
        Class method get_versioned_template_by_name finds a committed template
        by the name and version values passed.  It loads all of the template's
        information into the object's versioned_template attributes including
        its UUID, body and parameters.

        Parameters:
            name: The required template's name entered in Cisco DNAC.
                type: str
                default: none
                required: yes
            ver: The version of the template to be deployed.
                type: int
                default: 0
                required: yes

        Return Values:
            str: The requested template's contents.

        Usage:
            d = Dnac()
            t = Template(d, 'Set VLAN')
            d.api['Set VLAN'].getgetVersionedTemplateByName()
        """
        if not name:  # parameter name was not given a value
            name = self.__name  # use the Template's name
        # version must not be negative
        if ver < 0:
            raise DnacApiError(
                MODULE, 'get_versioned_template_by_name', ILLEGAL_VERSION,
                '', '', ver, '', LEGAL_VERSIONS
            )
        # reset the versioned template information
        self.__versioned_template = {}
        self.__versioned_template_id = ''
        self.__versioned_template_params = {}
        # find the versioned template by name
        templates = self.get_all_templates()
        if bool(templates):  # templates is not empty
            for template in templates:
                # find the versioned template by name and save its UUID
                if template['name'] == name:
                    versions = template['versionsInfo']
                    if ver > 0:
                        # get the version requested
                        for version in versions:
                            # DNAC uses a string for the version
                            if ver == int(version['version']):
                                # got it - set the versioned template id
                                # and move on
                                self.__versioned_template_id = version['id']
                                break
                            else:
                                # haven't found it - continue searching
                                continue
                        if not self.__versioned_template_id:
                            # version is greater than any versions
                            raise DnacApiError(
                                MODULE, 'get_versioned_template_by_name',
                                UNKNOWN_VERSION, '', '',
                                self.__versioned_template_id, '',
                                '%s version %i' % (name, ver)
                            )
                    elif ver == 0:
                        # get the latest version
                        latest = versions[0]
                        for version in versions:
                            if version['version'] <= latest['version']:
                                # not the latest version - keep going
                                continue
                            else:
                                # more recent version - save and continue
                                latest = version
                                continue
                        # got the latest version - save it
                        self.__version = latest['version']
                        self.__versioned_template_id = latest['id']
                else:  # keep looking for the template by its name
                    continue
            # get the versioned template using its id
            self.__versioned_template = \
                self.get_template_by_id(self.__versioned_template_id)
            # collect the template's parameters
            if bool(self.__versioned_template):  # template not empty
                params = self.__versioned_template['templateParams']
                if bool(params):  # parameter list is not empty
                    for param in params:
                        self.__versioned_template_params[param['parameterName']] = param['defaultValue']
                # otherwise there are no parameters - keep going
            else:
                raise DnacApiError(
                    MODULE, 'get_versioned_template_by_name', EMPTY_TEMPLATE,
                    '', '', str(self.__versioned_template), '',
                    '%s version %i' % (name, self.__versioned_template_id)
                )
        else:  # getAllTemplate failed to return any data
            raise DnacApiError(
                MODULE, 'get_versioned_template_by_name', NO_TEMPLATES_FOUND,
                '', '', str(templates), '', name
            )
        return self.__versioned_template

    # end get_versioned_template_by_name()

    def make_body(self):
        """
        The make_body method converts the Template object's target and
        versioned template information into a JSON encoded string used
        as the payload of a POST request to Cisco DNA Center.  Both
        deploy() and deploy_sync() already call this function.  It is
        unnecessary to use this method for pushing a template.

        Parameters:
            none

        Return Values:
            str: A JSON encoded string for deploying a CLI template.

        Usage:
            d = Dnac()
            template = Template(d, 'Enable CTS Interfaces')
            d.api['Enable CTS Interfaces'].make_body()
        """
        tgt_info = {
            'type': self.__target_type,
            'id': self.__target_id,
            'params': self.__versioned_template_params
        }
        target_info = [tgt_info]
        if self.dnac.version == '1.2.8':
            body = {
                'template_id': self.__versioned_template_id,
                'target_info': target_info
            }
        elif self.dnac.version == '1.2.10':
            body = {
                'templateId': self.__versioned_template_id,
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
        The deploy method asynchronously applies a template to a device.
        The Template's target information and versioned template data
        must be set prior to issuing this command.  The function creates
        a Deployment object, saves it, and then instructs it to perform
        a progress check on itself and then returns whatever Cisco DNA
        Center responds with.  Developers can then use the deployment
        instance to further monitor the job's success or failure.

        Parameters:
            none

        Return Values:
            str: The deployment job's current state.

        Usage:
            d = Dnac()
            template = Template(d, 'Create VRF')
            d.api['Create VRF'].target_id = '<router_uuid>'
            d.api['Create VRF'].target_type = TARGET_BY_ID
            print d.api['Create VRF'].deploy()
        """
        url = self.dnac.url + self.resource + '/deploy'
        if not self.__target_id:  # target_id is not set
            raise DnacApiError(
                MODULE, 'deploy', EMPTY_TEMPLATE, url,
                '', self.__target_id, '', NO_TEMPLATE_ID
            )
        if self.__target_type not in VALID_TARGET_TYPES:
            raise DnacApiError(
                MODULE, 'deploy', ILLEGAL_TARGET_TYPE, url,
                str(VALID_TARGET_TYPES), self.__target_type, '',
                '%s is not one of %s' % (self.__target_type,
                                         str(VALID_TARGET_TYPES))
            )
        body = self.make_body()
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
        deploy_id = ''
        if self.dnac.version == '1.2.8':
            did = results['response']['deploymentId']
            elts = did.split()
            deploy_id = elts[len(elts) - 1]
        # DNAC 1.2.10 uses a task that references a deploymentId in a string
        elif self.dnac.version == '1.2.10':
            task = {}
            taskUrl = '%s%s' % (self.dnac.url, results['response']['url'])
            task, status = self.crud.get(taskUrl,
                                         headers=self.dnac.hdrs,
                                         verify=self.verify,
                                         timeout=self.timeout)
            progress = task['response']['progress']
            progress_elts = progress.split(':')
            if progress_elts[3].find(TEMPLATE_ALREADY_DEPLOYED) != SUBSTR_NOT_FOUND:
                raise DnacApiError(
                    MODULE, 'deploy_sync', ALREADY_DEPLOYED, '',
                    '', str(body), status, ALREADY_DEPLOYED_RESOLUTION
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
        deploy_sync pushes a template to the target device and then waits
        for the job to finish.  By default, it checks the job every
        three seconds, but this can be set using the wait keyword argument.
        The Template's target information and versioned template data
        must be set prior to issuing this command.  deploy_sync creates
        a deployment object, saves it, and uses it to monitor the job's
        progress.  Upon completion, deploy_sync returns the job's status.

        Parameters:
            wait: The number of seconds before timing out Cisco DNAC's response.
                type: int
                default: 3
                required: no

        Return Values:
            str: The deployment job's current state.

        Usage:
            d = Dnac()
            template = Template(d, 'Create VRF')
            d.api['Create VRF'].target_id = '<router_uuid>'
            d.api['Create VRF'].target_type = TARGET_BY_ID
            print d.api['Create VRF'].deploy_sync()
        """
        url = self.dnac.url + self.resource + '/deploy'
        if not self.__target_id:  # target_id is not set
            raise DnacApiError(
                MODULE, 'deploy_sync', EMPTY_TEMPLATE, url,
                '', self.__target_id, '', NO_TEMPLATE_ID
            )
        if self.__target_type not in VALID_TARGET_TYPES:
            raise DnacApiError(
                MODULE, 'deploy_sync', ILLEGAL_TARGET_TYPE, url,
                str(VALID_TARGET_TYPES), self.__target_type, '',
                '%s is not one of %s' % (self.__target_type,
                                         str(VALID_TARGET_TYPES))
            )
        body = self.make_body()
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=body,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, 'deploy_sync', REQUEST_NOT_ACCEPTED, url,
                ACCEPTED, status, ERROR_MSGS[status], str(results)
            )
        # DNAC 1.2.8 references a deploymentId in a string
        deploy_id = ''
        if self.dnac.version == '1.2.8':
            did = results['response']['deploymentId']
            elts = did.split()
            deploy_id = elts[len(elts) - 1]
        # DNAC 1.2.10 uses a task that references a deploymentId in a string
        elif self.dnac.version == '1.2.10':
            task = {}
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
            progress_elts = progress.split(':')
            if progress_elts[3].find(TEMPLATE_ALREADY_DEPLOYED) != SUBSTR_NOT_FOUND:
                raise DnacApiError(
                    MODULE, 'deploy_sync', ALREADY_DEPLOYED, '',
                    '', str(body), status, ALREADY_DEPLOYED_RESOLUTION
                )
            deploy_id = progress_elts[len(progress_elts) - 1]
        else:
            raise DnacApiError(
                MODULE, 'deploy_sync', UNSUPPORTED_DNAC_VERSION, '',
                '', self.dnac.version, '', ''
            )
        self.__deployment = Deployment(self.dnac, deploy_id)
        self.__deployment.check_deployment()
        while self.__deployment.status == DEPLOYMENT_INIT:
            time.sleep(wait)
            self.__deployment.check_deployment()
        return self.__deployment.status


# end class Template()

# begin unit test


if __name__ == '__main__':

    from dnac.dnac import Dnac
    import time
    import pprint

    d = Dnac()
    pp = pprint.PrettyPrinter()
    t = Template(d, 'MGM Set VLAN')

    print('Template:')
    print()
    print(' type(t)                   = ' + str(type(t)))
    print(' name                      = ' + t.name)
    print(' resource                  = ' + t.resource)
    print(' template_id               = ' + t.template_id)
    print(' version                   = ' + str(t.version))
    print(' versioned_template        = ' + str(t.versioned_template))
    print(' versioned_template_id     = ' + t.versioned_template_id)
    print(' versioned_template_params = ' + str(t.versioned_template_params))
    print(' target_id                 = ' + t.target_id)
    print(' target_type               = ' + t.target_type)
    print(' deployment                = ' + t.deployment)
    print()

    # print 'Attempting to chance the template's name...'
    #
    # t.name = 'Throw an exception'
    #
    # sys.exit(0)

    print('Trying an earlier version of the template...')

    t = Template(d, 'MGM Set VLAN', version=1)

    print()
    print(' type(t)                   = ' + str(type(t)))
    print(' name                      = ' + t.name)
    print(' resource                  = ' + t.resource)
    print(' template_id               = ' + t.template_id)
    print(' version                   = ' + str(t.version))
    print(' versioned_template        = ' + str(t.versioned_template))
    print(' versioned_template_id     = ' + t.versioned_template_id)
    print(' versioned_template_params = ' + str(t.versioned_template_params))
    print(' target_id                 = ' + t.target_id)
    print(' target_type               = ' + t.target_type)
    print(' deployment                = ' + t.deployment)
    print()

    print('Resetting the template to the latest...')
    print()

    t = Template(d, 'MGM Set VLAN')

    print('Setting the versioned template\'s parameters...')
    print()
    print(' version                   = ' + str(t.version))
    print(' versioned_template        = ' + str(t.versioned_template))
    print(' versioned_template_id     = ' + t.versioned_template_id)
    print(' versioned_template_params = ')
    pp.pprint(t.versioned_template_params)
    print()

    t.versioned_template_params['interface'] = 'gig1/0/1'
    t.versioned_template_params['description'] = 'Configured by template.py'
    t.versioned_template_params['vlan'] = 60

    print(' interface   = ' + t.versioned_template_params['interface'])
    print(' description = ' + t.versioned_template_params['description'])
    print(' vlan        = ' + str(t.versioned_template_params['vlan']))
    print()
    print('Build the request body...')
    print()

    t.target_id = 'a0116157-3a02-4b8d-ad89-45f45ecad5da'
    t.target_type = TARGET_BY_ID
    body = t.make_body()

    print(' body = ')
    pp.pprint(body)
    print()
    print('Deploying the template asynchronously...')
    print()

    status = t.deploy()

    print(' status           = ' + str(status))
    print(' type(deployment) = ' + str(t.deployment))
    print(' deployment.name  = ' + t.deployment.name)
    print(' deployment.id    = ' + t.deployment.id)
    print()
    print('Checking deployment...')

    while status == DEPLOYMENT_INIT:
        print(' status = ' + status)
        time.sleep(1)
        status = t.deployment.check_deployment()

    print(' status          = ' + status)
    print(' results[status] = ' + t.deployment.results['status'])
    print(' results         = ')
    pp.pprint(t.deployment.results)
    print()
    print('Template: unit test complete.')
    print()
