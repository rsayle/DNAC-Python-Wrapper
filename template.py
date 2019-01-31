#!/user/bin/env python

from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnacapi import DnacApi, \
                    DnacApiError
from crud import OK, \
                 REQUEST_NOT_OK, \
                 ACCEPTED, \
                 REQUEST_NOT_ACCEPTED, \
                 ERROR_MSGS
from deployment import Deployment
import json
import time

## globals

MODULE="template.py"

# values instructing Cisco DNA Center how to interpret the target ID value
TARGET_BY_DEFAULT="DEFAULT"
TARGET_BY_ID="MANAGED_DEVICE_UUID"
TARGET_BY_HOSTNAME="MANAGED_DEVICE_HOSTNAME"
TARGET_BY_IP="MANAGED_DEVICE_IP"
TARGET_BY_SERIAL="PRE_PROVISIONED_SERIAL"
TARGET_BY_MAC="PRE_PROVISIONED_SERIAL"

VALID_TARGET_TYPES=[TARGET_BY_DEFAULT, \
                    TARGET_BY_ID, \
                    TARGET_BY_HOSTNAME, \
                    TARGET_BY_IP, \
                    TARGET_BY_SERIAL, \
                    TARGET_BY_MAC]

# deployment states returned when checking on a deployment's status
DEPLOYMENT_INIT="INIT"
DEPLOYMENT_SUCCESS="SUCCESS"
DEPLOYMENT_FAILURE="FAILURE"

VALID_DEPLOYMENT_STATES=[DEPLOYMENT_INIT, \
                         DEPLOYMENT_SUCCESS, \
                         DEPLOYMENT_FAILURE]

## end globals

## error messages

TEMPLATE_NOT_FOUND="Could not find template"
NO_TEMPLATE_ID="The template ID is empty or does not exist"
NO_TEMPLATES_FOUND="Could not retrieve any templates"
INVALID_RESPONSE="Invalid response to API call"
EMPTY_TEMPLATE="Template has no data or does not exist"
EMPTY_TARGET="Template target ID is not set"
ILLEGAL_TARGET_TYPE="Illegal template target type"
UNKNOWN_DEPLOYMENT_STATUS="Unknown deployment status"
ALREADY_DEPLOYED="Template already deployed"
ILLEGAL_VERSION="Illegal template version"
LEGAL_VERSIONS="Template version must be 0 or greater. Use 0 to signal this API wrapper to use the latest version automatically."
UNKNOWN_VERSION="Unknown template version"
ILLEGAL_NAME_CHANGE="Changing a template's name is prohibited"
ILLEGAL_NAME_CHANGE_RESOLUTION="Create a new Template object using a different template's name"

## end error messages

class Template(DnacApi):
    '''
    Class Template provides an abstraction of CLI templates in Cisco's
    DNA Center.  Once a network device has first been provisioned in
    Cisco DNAC, it's configuration can be updated with a CLI template.
    This class encapsulates the API calls and tools required to deploy
    a configuration template.

    A Template object's name must match the name it is given in a Cisco
    DNAC cluster.  You do not necessarily need to know in which project
    it is listed, but the name must be the same.  Be careful: template
    names in Cisco DNA Center are case sensitive.

    Changing a template's name is prohibited by this class.  The very
    purpose of this python package is to make it easy to use Cisco DNA
    Center's APIs.  For this class, Template automatically handles finding
    and loading a template by its name and the requested version; however,
    a problem could arise if a template's name is changed but its version
    is not available in Cisco DNA Center.  This class, therefore, overrides
    its parent class name setter method and raises an exception whenever
    an attempt to change a Template object's name occurs.  Doing so,
    gives developers the ability to select and work with different versions
    of a template using the same object at the expense of being able to
    point the object at a different template.  If work must be done with
    a different template in Cisco DNAC, create a new Template object with
    a new template's name

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
    list of target devices upon which to apply it, deployment jobs do not
    necessarily complete immediately.  The Template class creates and holds
    a Deployment object for monitoring the job's status.  This happens
    automatically whenever the deploy() or deploySync() methods are called.

    Attributes:
        dnac:
            Dnac object: A reference to the Dnac instance that contains
                         the Template object
            default: None
        name:
            str: A user friendly name for the Template object that is
                 used both as a key for finding it in a Dnac.api attribute
                 and for locating the real CLI template in Cisco DNAC.
                 The template name must match its name in Cisco DNAC
                 exactly including its case.
            default: None
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
        templateId:
            str: The UUID in Cisco DNAC of the base template.  A base
                 template cannot be deployed on any equipment.
            default: None
            scope: protected
        versionedTemplate:
            dict: The CLI template as represented in Cisco DNA Center.
            default: None
            scope: protected
        versionedTemplateId:
            str: The UUID in Cisco DNAC of committed template, which can
                 be deployed.
            default: None
            scope: protected
        versionedTemplateParams:
            dict: A dictionary whose keys are the template's parameter
                  names.  Their values can each be set directly through
                  accessing this dictionary.  See the example below in
                  the Usage section.
            default: None
            scope: protected
        targetId:
            str: The UUID of a network device to which the template
                 will be applied.
            default: None
        targetType:
            str: An enumerated value that instructs Cisco DNA Center how
                 to find the device so that the template can be applied.
                 Legal values for targetType are kept in the global
                 list:
                    VALID_TARGET_TYPES=[TARGET_BY_DEFAULT,
                                        TARGET_BY_ID,
                                        TARGET_BY_HOSTNAME,
                                        TARGET_BY_IP,
                                        TARGET_BY_SERIAL,
                                        TARGET_BY_MAC]
            default: TARGET_BY_DEFAULT
        deployment:
            Deployment object: A Deployment instance that provides the
                               deploy job's status and the job's results.
            default: None
            scope: protected
    Usage:
        d = Dnac()
        template = Template(d, "Set VLAN")
        d.api['Set VLAN'].targetId = <switch_uuid>
        d.api['Set VLAN'].versionedTemplateParams['interface'] = "gig1/0/1"
        d.api['Set VLAN'].versionedTemplateParams['vlan'] = 10
        d.api['Set VLAN'].deploySync()
        print str(template.deployment.results)
    '''
    def __init__(self,
                 dnac,
                 name,
                 version=0,
                 verify=False,
                 timeout=5):
        '''
        Template's __init__ method constructs a new Template object.
        It automatically searches for the template in Cisco DNA Center
        by the Template's name.  If found, then it will search for the
        committed version of the template according to the value passed
        in the version keyword argument.  If no version is selected, it
        chooses the latest version available.

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: None
                required: Yes
            name: The template's exact name, including its case, in
                  Cisco DNA Center.
                type: str
                default: None
                required: Yes
            version: The template version that will be deployed.  When set
                     to zero, Template selects the latest version.
                type: int
                default: 0
                required: No
            verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: No
            timeout: The number of seconds to wait for Cisco DNAC's
                     response.
                type: int
                default: 5
                required: No

        Return Values:
            Template object: a newly build Template instance.

        Usage:
            d = Dnac()
            template = Template(d, "Enable BGP", version=5)
        '''
        # version is the template's version and must not be negative
        if version < 0:
            raise DnacApiError(
                MODULE, "__init__", ILLEGAL_VERSION, "", "",
                version, "", LEGAL_VERSIONS
                              )
        # check Cisco DNA Center's version and set the resource path
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = "/dna/intent/api/v1/template-programmer/template"
        else:
            raise DnacError(
                "__init__: %s: %s" %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                               )
        # setup initial attribute values
        self.__templateId = "" # base template ID
        self.__version = version # requested template version, 0 = latest
        self.__versionedTemplate = {} 
        self.__versionedTemplateId = "" # template that can be deployed
        self.__versionedTemplateParams = {}
        self.__targetId = "" # where to deploy the template
        self.__targetType = TARGET_BY_DEFAULT # how to find the target
        self.__deployment = "" # object for monitoring the deployment
        super(Template, self).__init__(dnac,
                                       name,
                                       resource=path,
                                       verify=verify,
                                       timeout=timeout)
        # retrieve the template ID by its name
        self.__templateId = self.getTemplateIdByName(self.name)
        if not self.__templateId: # template could not be found
            raise DnacApiError(
                MODULE, "__init__", TEMPLATE_NOT_FOUND, "",
                "", self.__templateId, "", ""
                              )
        # retrieve the versioned template
        #   getVersionedTemplateByName sets self.__versionedTemplate
        self.getVersionedTemplateByName(self.name, self.__version)
        if not bool(self.__versionedTemplate): # template is empty
            # getVersionedTemplateByName should catch this condition, but
            # just in case, here's another integrity check
            raise DnacApiError(
                MODULE, "__init__", UNKNOWN_VERSION, "",
                "", self.__versionedTemplate, "",
                "%s version %i" % (self.name, self.__version)
                              )

## end __init__()

## override DnacApi's name setter

    @DnacApi.name.setter
    def name(self, name):
        '''
        Changing a template's name is prohibited by this class.  The very
        purpose of this python package is to make it easy to use Cisco DNA
        Center's APIs.  For this class, Template automatically handles
        finding and loading a template by its name and the requested
        version; however, a problem could arise if a template's name is
        changed but its version is not available in Cisco DNA Center.
        This class, therefore, overrides its parent class name setter
        method and raises an exception whenever an attempt to change a
        Template object's name occurs.  Doing so, gives developers the
        ability to select and work with different versions of a template
        using the same object at the expense of being able to point the
        object at a different template.  If work must be done with a
        different template in Cisco DNAC, create a new Template object with
        the new template's name
        '''
        raise DnacApiError(
            MODULE, "name setter", ILLEGAL_NAME_CHANGE, "",
            "", name, "", ILLEGAL_NAME_CHANGE_RESOLUTION
                          )

## end override DnacApi's name setter

    @property
    def templateId(self):
        '''
        Get method templateId returns the base template's UUID from Cisco
        DNA Center.

        Parameters:
            None

        Return Values:
            str: The template's UUID.

        Usage:
            d = Dnac()
            template = Template(d, "Add Loopback")
            print (d.api['Add Loopback'].templateId)
        '''
        return self.__templateId

## end templateId getter

    @property
    def version(self):
        '''
        The version get method returns the template's version number.

        Parameters:
            None

        Return Value:
            int: The template's version number.

        Usage:
            d = Dnac()
            template = Template(d, "Add Loopback")
            print d.api['Add Loopback'].version
        '''
        return self.__version

## end version getter

    @version.setter
    def version(self, version):
        '''
        The version set method changes the desired version of the template
        to be deployed.  This method also updates the versioned template,
        its UUID and its parameters in this class' respective attributes.
        See class method getVersionedTemplateByName for details.  If the
        requested version does not exist, an exception is thrown.

        Parameters:
            int: The new template version.

        Return Values:
            None

        Usage:
            d = Dnac()
            template = Template(d, "Set VLAN")
            template.version = 5
        '''
        self.__version = version
        # reload versioned template info using getVersionedTemplateByName
        self.getVersionedTemplateByName(self.name, self.__version)
        # if the version requested does not exist, raise an exception
        if not bool(self.__versionedTemplate): # template is empty
            # getVersionedTemplateByName should catch this condition, but
            # just in case, here's another integrity check
            raise DnacApiError(
                MODULE, "version setter", UNKNOWN_VERSION, "",
                "", self.__versionedTemplate, "",
                "%s version %i" % (self.name, version)
                              )

## end version setter

    @property
    def versionedTemplate(self):
        '''
        The versionedTemplate get method returns the template's contents.

        Parameters:
            None

        Return Value:
            dict: The template's data.

        Usage:
            d = Dnac()
            template = Template(d, "Add Loopback")
            print str(d.api['Add Loopback'].versionedTemplate)
        '''
        return self.__versionedTemplate

## end versionedTemplate getter

    @property
    def versionedTemplateId(self):
        '''
        The versionedTemplateId get method returns the UUID for the
        committed template based upon the object's current template version.

        Parameters:
            None

        Return Value:
            str: The versioned template's UUID in Cisco DNA Center

        Usage:
            d = Dnac()
            template = Template(d, "Add Loopback")
            print d.api['Add Loopback'].versionedTemplateId
        '''
        return self.__versionedTemplateId

## end versionedTemplateId getter

    @property
    def versionedTemplateParams(self):
        '''
        versionedTemplateParams returns the template's parameters
        dictionary.  Values may be updated directly by accessing this
        attribute.

        Parameters:
            None

        Return Value:
            dict: The template's parameters and their currnt values.

        Usage:
            d = Dnac()
            template = Template(d, "Add Loopback")
            print str(d.api['Add Loopback'].versionedTemplateParams)
            d.api['Add Loopback'].versionedTemplateParams['ip'] = 10.1.1.1
        '''
        return self.__versionedTemplateParams

## end versionedTemplateParams getter

    @property
    def targetId(self):
        '''
        Template's targetId get method returns the UUID of the managed
        device where the template will be applied.

        Parameters:
            None

        Return Values:
            str: A Cisco DNAC managed device's UUID.

        Usage:
            d = Dnac()
            template = Template(d, "Add Loopback")
            print d.api['Add Loopback'].targetId
        '''
        return self.__targetId

## end targetId getter

    @targetId.setter
    def targetId(self, targetId):
        '''
        Method targetId sets the value to the UUID of the network device
        where the template will be applied.

        Parameters:
            targetId:
                type: str
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            d = Dnac()
            template = Template(d, "Enable EIGRP")
            d.api['Enable EIGRP'].targetId = "<router_UUID>"
        '''
        self.__targetId = targetId

## end targetId setter

    @property
    def targetType(self):
        '''
        Template's targetType get method returns the value used to instruct
        Cisco DNAC how to find targetted device in it inventory when
        applying a CLI template.

        Parameters:
            None

        Return Values:
            str: One of the following enumerated values:
                TARGET_BY_DEFAULT="DEFAULT"
                TARGET_BY_ID="MANAGED_DEVICE_UUID"
                TARGET_BY_HOSTNAME="MANAGED_DEVICE_HOSTNAME"
                TARGET_BY_IP="MANAGED_DEVICE_IP"
                TARGET_BY_SERIAL="PRE_PROVISIONED_SERIAL"
                TARGET_BY_MAC="PRE_PROVISIONED_SERIAL"

        Usage:
            d = Dnac()
            template = Template(d, "Set VLAN")
            print d.api['Set VLAN'].targetType
        '''
        return self.__targetType

## end targetType getter

    @targetType.setter
    def targetType(self, targetType):
        '''
        Set method targetType changes the desired method that Cisco DNA
        Center uses to find a device in its inventory in order to apply
        the template.

        Paramters:
            targetType:
                str: one of the following enumerated values:
                    TARGET_BY_DEFAULT="DEFAULT"
                    TARGET_BY_ID="MANAGED_DEVICE_UUID"
                    TARGET_BY_HOSTNAME="MANAGED_DEVICE_HOSTNAME"
                    TARGET_BY_IP="MANAGED_DEVICE_IP"
                    TARGET_BY_SERIAL="PRE_PROVISIONED_SERIAL"
                    TARGET_BY_MAC="PRE_PROVISIONED_SERIAL"
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            d = Dnac()
            template = Template(d, "Set VLAN")
            d.api['Set VLAN'].targetType = TARGET_BY_HOSTNAME
        '''
        self.__targetType = targetType

## end targetType setter

    @property
    def deployment(self):
        '''
        The deployment get method returns a reference to the Template's
        deploy job.  Use this attribute to monitor the job's status and
        get its results.

        Parameters:
            None

        Return Values:
            Deployment object: The job for the deployed template.

        Usage:
            d = Dnac()
            template = Template(d, "Set VLAN")
            print str(d.api['Set Vlan'].deployment.results)
        '''
        return self.__deployment

## end deployment getter

    def getAllTemplates(self):
        '''
        Class method getAllTemplates queries the Cisco DNA Center cluster
        for a listing of every template it has.  The listing includes
        the base templates and all of its versions.

        Parameters:
            None

        Return Values:
            list: A listing of all available templates.

        Usage:
            d = Dnac()
            template = Template(d, "Set VLAN")
            print str(d.api['Set Vlan'].getAllTemplates)
        '''
        url = self.dnac.url + self.resource
        templates, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, "getAllTemplates", REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(results)
                              )
        return templates

## end getAllTemplates()

    def getTemplateById(self, id):
        '''
        getTemplateById pulls the template information for the one
        specified by the UUID passed to the function.  Either base or
        versioned templates may be queried.

        Parameters:
            id: The UUID of a template.
                type: str
                default: None
                required: Yes

        Return Values:
            dict: The template's data.

        Usage:
            d = Dnac()
            template = Template(d, "Set VLAN")
            print str(d.api['Set Vlan'].getTemplateById("<template_uuid>")
        '''
        url = self.dnac.url + self.resource + "/" + id
        template, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, "getTemplateById", REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(results)
                              )
        return template

## end getTemplateById

    def getTemplateIdByName(self, name=""):
        '''
        getTemplateIdByName finds the base template by its name and
        saves the value in its __templateId attribute and returns it.

        Parameters:
            name: The template's name, which must match exactly as it
                  is entered in Cisco DNA Center.  If no name is given,
                  the method defaults to the Template object's own name.
                type: str
                default: The Template object's name.
                required: No

        Return Values:
            str: The template's UUID.

        Usage:
            d = Dnac()
            template = Template(d, "Set VLAN")
            print str(d.api['Set Vlan'].getTemplateByIdByName()
        '''
        if not name: # parameter name was not given a value
            name = self.__name # use the Template's name
        self.__templateId = ""
        # find the template by name
        templates = self.getAllTemplates()
        if bool(templates): # templates is not empty
            for template in templates:
                # find the template by name, save it and save its ID
                if template['name'] == name:
                    self.__templateId = template['templateId']
                else: # keep looking for the template by its name
                    continue
        else:
            raise DnacApiError(
                MODULE, "getTemplateIdByName", NO_TEMPLATES_FOUND, "",
                "", "", "", ""
                              )
        # all done - return the template's UUID
        return self.__templateId

## end getTemplateByName()

    def getVersionedTemplateByName(self, name="", ver=0):
        '''
        Class method getVersionedTemplateByName finds a committed template
        by the name and ver values passed.  It loads all of the template's
        information into the object's versionedTemplate attributes including
        its UUID, body and parameters.

        Parameters:
            name: The required template's name entered in Cisco DNAC.
                type: str
                default: The Template object's name.
                required: No
            ver: The version of the template to be deployed.
                type: int
                default: The latest version available.
                required: No

        Return Values:
            str: The requested template's contents.

        Usage:
            d = Dnac()
            t = Template(d, 'Set VLAN')
            d.api['Set VLAN'].getgetVersionedTemplateByName()
        '''
        if not name: # parameter name was not given a value
            name = self.__name # use the Template's name
        # version must not be negative
        if ver < 0:
            raise DnacApiError(
                MODULE, "getVersionedTemplateByName", ILLEGAL_VERSION,
                "", "", version, "", LEGAL_VERSIONS
                              )
        # reset the versioned template information
        self.__versionedTemplate = {}
        self.__versionedTemplateId = ""
        self.__versionedTemplateParams = {}
        # find the versioned template by name
        templates = self.getAllTemplates()
        if bool(templates): # templates is not empty
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
                                self.__versionedTemplateId = version['id']
                                break
                            else:
                                # haven't found it - continue searching
                                continue
                        if not self.__versionedTemplateId:
                            # version is greater than any versions
                            raise DnacApiError(
                                MODULE, "getVersionedTemplateByName",
                                UNKNOWN_VERSION, "", "", 
                                self.__versionedTemplateId, "",
                                "%s version %i" % (name, ver)
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
                        self.__versionedTemplateId = latest['id']
                else: # keep looking for the template by its name
                    continue
            # get the versioned template using its id
            self.__versionedTemplate = \
                self.getTemplateById(self.__versionedTemplateId)
            # collect the template's parameters
            if bool(self.__versionedTemplate): # template not empty
                params = self.__versionedTemplate['templateParams']
                if bool(params): # parameter list is not empty
                    for param in params:
                        self.__versionedTemplateParams\
                            [param['parameterName']] = \
                             param['defaultValue']
                # otherwise there are no parameters - keep going
            else:
                raise DnacApiError(
                    MODULE, "getVersionedTemplateByName", EMPTY_TEMPLATE,
                    "", "", str(self.__versionedTemplate), "",
                    "%s version %i" % (name, self.__versionedTemplateId)
                                  )
        else: # getAllTemplate failed to return any data
            raise DnacApiError(
                MODULE, "getVersionedTemplateByName", NO_TEMPLATES_FOUND,
                "", "", str(templates), "", name
                              )
        return self.__versionedTemplate

## end getVersionedTemplateByName()

    def makeBody(self):
        '''
        The makeBody method converts the Template object's target and
        versioned template information into a JSON encoded string used
        as the payload of a POST request to Cisco DNA Center.  Both
        deploy() and deploySync() already call this function.  It is
        unnecessary to use this method for pushing a template.

        Parameters:
            None

        Return Values:
            str: A JSON encoded string for deploying a CLI template.
        
        Usage:
            d = Dnac()
            template = Template(d, "Enable CTS Interfaces")
            d.api['Enable CTS Interfaces'].makeBody()
        '''
        tgtinfo = {}
        tgtinfo['type'] = self.__targetType
        tgtinfo['id'] = self.__targetId
        tgtinfo['params'] = self.__versionedTemplateParams
        targetInfo = []
        targetInfo.append(tgtinfo)
        body = {}
        body['templateId'] = self.__versionedTemplateId
        body['targetInfo'] = targetInfo
        return json.dumps(body)

## end makeBody()

    def deploy(self):
        '''
        The deploy method asynchronously applies a template to a device.
        The Template's target information and versioned template data
        must be set prior to issuing this command.  The function creates
        a Deployment object, saves it, and then instructs it to perform
        a progress check on itself and then returns whateved Cisco DNA
        Center reponds with.  Developers can then use the deployment
        instance to further monitor the job's success or failure.

        Parameters:
            None

        Return Values:
            str: The deployment job's current state.

        Usage:
            d = Dnac()
            template = Template(d, "Create VRF")
            d.api['Create VRF'].targetId = "<router_uuid>"
            d.api['Create VRF'].targetType = TARGET_BY_ID
            print d.api['Create VRF'].deploy()
        '''
        url = self.dnac.url + self.resource + "/deploy"
        if not self.__targetId: # targetId is not set
            raise DnacApiError(
                MODULE, "deploy", EMPTY_TEMPLATE, url,
                "", self.__targetId, "", NO_TEMPLATE_ID
                              )
        if self.__targetType not in VALID_TARGET_TYPES:
            raise DnacApiError(
                MODULE, "deploy", ILLEGAL_TARGET_TYPE, url,
                str(VALID_TARGET_TYPES), self.__targetType, "",
                "%s is not one of %s" % (self.__targetType,
                str(VALID_TARGET_TYPES))
                              )
        body = self.makeBody()
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=body,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, "checkDeployment", REQUEST_NOT_ACCEPTED, url,
                ACCEPTED, status, ERROR_MSGS[status], str(results)
                              )
        # make a deployment object
        did = results['deploymentId']
        elts = did.split()
        deployId = elts[len(elts) - 1]
        self.__deployment = Deployment(self.dnac, 
                                       "deployment_", 
                                       id=deployId)
        return self.__deployment.checkDeployment()

## end deploy()

    def deploySync(self, wait=3):
        '''
        deploySync pushes a template to the target device and then waits
        for the job to finish.  By default, it checks the job every
        three seconds, but this can be set using the wait keyword argument.
        The Template's target information and versioned template data
        must be set prior to issuing this command.  deploySync creates
        a deployment object, saves it, and uses it to monitor the job's
        progress.  Upon completion, deploySync returns the job's status.

        Parameters:
            None

        Return Values:
            str: The deployment job's current state.

        Usage:
            d = Dnac()
            template = Template(d, "Create VRF")
            d.api['Create VRF'].targetId = "<router_uuid>"
            d.api['Create VRF'].targetType = TARGET_BY_ID
            print d.api['Create VRF'].deploySync()
        '''
        url = self.dnac.url + self.resource + "/deploy"
        if not self.__targetId: # targetId is not set
            raise DnacApiError(
                MODULE, "deploySync", EMPTY_TEMPLATE, url,
                "", self.__targetId, "", NO_TEMPLATE_ID
                              )
        if self.__targetType not in VALID_TARGET_TYPES:
            raise DnacApiError(
                MODULE, "deploySync", ILLEGAL_TARGET_TYPE, url,
                str(VALID_TARGET_TYPES), self.__targetType, "",
                "%s is not one of %s" % (self.__targetType,
                str(VALID_TARGET_TYPES))
                              )
        body = self.makeBody()
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=body,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, "checkDeployment", REQUEST_NOT_ACCEPTED, url,
                ACCEPTED, status, ERROR_MSGS[status], str(results)
                              )
        # make a deployment object
        did = results['deploymentId']
        elts = did.split()
        deployId = elts[len(elts) - 1]
        self.__deployment = Deployment(self.dnac,
                                       "deployment_",
                                       id=deployId)
        self.deployment.checkDeployment()
        while self.deployment.status == DEPLOYMENT_INIT:
            time.sleep(wait)
            self.deployment.checkDeployment()
        return self.deployment.status

## end class Template()

## begin unit test

if __name__ == '__main__':

    from dnac import Dnac
    import time
    import sys

    d = Dnac()
    t = Template(d, "MGM Set VLAN")

    print "Template:"
    print 
    print " type(t)                 = " + str(type(t))
    print " name                    = " + t.name
    print " resource                = " + t.resource
    print " templateId              = " + t.templateId
    print " version                 = " + str(t.version)
    print " versionedTemplate       = " + str(t.versionedTemplate)
    print " versionedTemplateId     = " + t.versionedTemplateId
    print " versionedTemplateParams = " + str(t.versionedTemplateParams)
    print " targetId                = " + t.targetId
    print " targetType              = " + t.targetType
    print " deployment              = " + t.deployment
    print

    #print "Attempting to chance the template's name..."
    #
    #t.name = "Throw an exception"
    #
    #sys.exit(0)
    
    print "Trying an earlier version of the template..."

    t = Template(d, "MGM Set VLAN", version=1)

    print 
    print " type(t)                 = " + str(type(t))
    print " name                    = " + t.name
    print " resource                = " + t.resource
    print " templateId              = " + t.templateId
    print " version                 = " + str(t.version)
    print " versionedTemplate       = " + str(t.versionedTemplate)
    print " versionedTemplateId     = " + t.versionedTemplateId
    print " versionedTemplateParams = " + str(t.versionedTemplateParams)
    print " targetId                = " + t.targetId
    print " targetType              = " + t.targetType
    print " deployment              = " + t.deployment
    print

    print "Resetting the template to the latest..."
    print

    t = Template(d, "MGM Set VLAN")

    print "Setting the versioned template's parameters..."
    print
    print " version                 = " + str(t.version)
    print " versionedTemplate       = " + str(t.versionedTemplate)
    print " versionedTemplateId     = " + t.versionedTemplateId
    print " versionedTemplateParams = " + str(t.versionedTemplateParams)
    print

    t.versionedTemplateParams['interface'] = "gig1/0/1"
    t.versionedTemplateParams['description'] = "Configured by template.py"
    t.versionedTemplateParams['vlan'] = 60

    print " interface   = " + t.versionedTemplateParams['interface']
    print " description = " + t.versionedTemplateParams['description']
    print " vlan        = " + str(t.versionedTemplateParams['vlan'])
    print
    print "Build the request body..."
    print

    t.targetId = "a0116157-3a02-4b8d-ad89-45f45ecad5da"
    t.targetType = TARGET_BY_ID
    body = t.makeBody()

    print " body = " + body
    print
    print "Deploying the template asynchronously..."
    print

    status = t.deploy()

    print " status           = " + str(status)
    print " type(deployment) = " + str(t.deployment)
    print " deployment.name  = " + t.deployment.name
    print " deployment.id    = " + t.deployment.id
    print
    print "Checking deployment..."
    
    while status == DEPLOYMENT_INIT:
        print " status = " + status
        time.sleep(1)
        status = t.deployment.checkDeployment()

    print " status          = " + status
    print " results[status] = " + t.deployment.results['status']
    print " results         = " + str(t.deployment.results)
    print
    print "Template: unit test complete."

