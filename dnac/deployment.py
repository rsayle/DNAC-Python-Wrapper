
from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import ACCEPTED, \
                      REQUEST_NOT_ACCEPTED, \
                      ERROR_MSGS

MODULE = 'deployment.py'

# globals

DEPLOYMENT_RESOURCE_PATH = {
    '1.2.8': '/api/v1/template-programmer/template/deploy/status',
    '1.2.10': '/api/v1/template-programmer/template/deploy/status',
    '1.3.0.2': '/api/v1/template-programmer/template/deploy/status',
    '1.3.0.3': '/api/v1/template-programmer/template/deploy/status',
    '1.3.1.3': '/api/v1/template-programmer/template/deploy/status',
    '1.3.1.4': '/dna/intent/api/v1/template-programmer/template/deploy/status/'
}

STATUS_KEY = 'status'

NO_STATUS = ''

class Deployment(DnacApi):
    """
    The Deployment class monitors Cisco DNA Center's progress when pushing
    a template to a set of devices.  When using a Template object to
    apply changes, the Template automatically creates and stores a
    corresponding Deployment instance.  Use the Template to reference the
    Deployment for the job's results.

    Usage:
        d = Dnac()
        template = Template(d, 'Set VLAN')
        d.api['Set VLAN'].deploy()
        print d.api['Set VLAN'].deployment.check_deployment()
    """

    def __init__(self,
                 dnac,
                 deployment_id,
                 verify=False,
                 timeout=5):
        """
        Creates a deployment object and sets the deployment job's UUID.

        :param dnac: A reference to the master Dnac instance.
            type: Dnac object
            required: yes
            default: None
        :param deployment_id: The deployment job's UUID.
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
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = DEPLOYMENT_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError(
                '__init__: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                           )
        self.__deployment = {}
        self.__deployment_id = deployment_id
        super(Deployment, self).__init__(dnac,
                                         ('deployment_%s' % deployment_id),
                                         resource=path,
                                         verify=verify,
                                         timeout=timeout)

    # end __init__()

    @property
    def deployment_id(self):
        """
        Provides the deployment job's UUID.
        :return: str
        """
        return self.__deployment_id

    # end id getter

    @property
    def status(self):
        """
        When available, reports the deployment job's status: SUCCESS or FAILURE.  Returns an empty string if the job
        has not yet completed.
        :return: str
        """
        if STATUS_KEY in self.__deployment.keys():
            return self.__deployment[STATUS_KEY]
        else:
            return NO_STATUS

    # end status getter

    def check_deployment(self):
        """
        Makes an API call to Cisco DNA Center for the deployment job's results.
        :return: dict
        """
        # prepare the API call
        url = '%s%s/%s' % (self.dnac.url, self.resource, self.__deployment_id)
        # make the call
        results, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        # return the results
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, 'check_deployment', REQUEST_NOT_ACCEPTED, url,
                ACCEPTED, status, ERROR_MSGS[status], str(results)
                              )
        self.__deployment = results
        return self.__deployment

    # end check_deployment()

# end class Deployment()
