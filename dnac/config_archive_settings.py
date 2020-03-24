from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS
import json

MODULE = 'config_archive_settings.py'

ARCHIVE_SETTINGS_RESOURCE_PATH = {
    '1.2.10': '/api/v1/archive-config/setting',
    '1.3.0.2': '/api/v1/archive-config/setting',
    '1.3.0.3': '/api/v1/archive-config/setting',
    '1.3.1.3': '/api/v1/archive-config/setting',
    '1.3.1.4': '/api/v1/archive-config/setting'
}

# globals

SUCCESSFUL_ARCHIVE_SETTINGS_UPDATE = 'SUCCESS'


class ConfigArchiveSettings(DnacApi):
    """
    The ConfigArchiveSettings class stores and modifies Cisco DNA Center's archive settings.  Archive settings are
    global across a given Cisco DNAC cluster.  The available settings are:

        noOfDays - the number of days to keep a device's configuration archive
        noOfVersion - the maximum number of archive versions for a given device
        timeout - timeout value for constructing a new device archive

    Cisco DNAC's API uses these as the keys of a dict when returning the existing settings or receiving a request
    to change the settings.

    Attributes:
        dnac: A pointer to the Dnac object containing the ConfigArchiveSettings instance.
            type: Dnac object
            default: none
            scope: protected
        name: A user-friendly name for accessing the ConfigArchiveSettings object in a Dnac.api{}.
            type: str
            default: none
            scope: protected
        settings: The archive's settings.
            type: dict
            default: {}
            scope: public
        resource: The URI for running commands within Cisco DNAC.
            type: str
            default: Cisco DNA Center version dependent
            scope: protected
        verify: A flag indicating whether or not to verify Cisco DNA Center's certificate.
            type: bool
            default: False
            scope: protected
        timeout: The number of seconds to wait for Cisco DNAC to respond before timing out.
            type: int
            default: 5
            scope: protected

    Usage:
        d = Dnac()
        archive_settings = ConfigArchiveSettings(d, d.name)
        print(archive_settings.settings)
    """

    def __init__(self,
                 dnac,
                 name,
                 verify=False,
                 timeout=5):
        """
        The ConfigArchiveSettings __init__ method creates a new object with blank settings.
        :param dnac: A reference to the containing Dnac object.
            type: Dnac object
            default: none
            required: yes
        :param name: A user friendly name for finding this object in a Dnac instance.
            type: str
            default: none
            required: yes
        :param verify: A flag used to check Cisco DNAC's certificate.
            type: boolean
            default: False
            required: no
        :param timeout: The number of seconds to wait for Cisco DNAC's response.
            type: int
            default: 5
            required: no
        """
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = ARCHIVE_SETTINGS_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError(
                '__init__: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                           )
        self.__settings = {}  # global DNA Center archive settings
        super(ConfigArchiveSettings, self).__init__(dnac,
                                                    '%s_archive_settings' % name,
                                                    resource=path,
                                                    verify=verify,
                                                    timeout=timeout)

    # end __init__()

    @property
    def settings(self):
        """
        The settings getter method makes a call to the Cisco DNAC cluster, stores the results in the __settings
        attribute and then returns value to the calling program.
        :return: dict
        """
        # make a GET call to DNAC for the current settings
        url = self.dnac.url + ARCHIVE_SETTINGS_RESOURCE_PATH[self.dnac.version]
        settings, status = self.crud.get(url,
                                         headers=self.dnac.hdrs,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'settings getter', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(settings)
                              )
        self.__settings = settings
        return self.__settings

    # end settings getter

    @settings.setter
    def settings(self, settings):
        """
        The settings setter method changes the objects value for its __settings attribute.
        :param settings: The new archive settings for the Cisco DNA Center instance.
            type: dict
            default: none
            required: yes
        :return: none
        """
        self.__settings = settings
        url = self.dnac.url + ARCHIVE_SETTINGS_RESOURCE_PATH[self.dnac.version]
        result, status = self.crud.post(url,
                                        headers=self.dnac.hdrs,
                                        body=json.dumps(self.__settings),
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'settings setter', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(self.__settings)
            )
        if result['status'] != SUCCESSFUL_ARCHIVE_SETTINGS_UPDATE:
            print('Did not work')

    # end settings setter

# end class ConfigArchiveSettings
