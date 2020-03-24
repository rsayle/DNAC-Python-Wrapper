from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS
from dnac.file import File
from dnac.task import Task

# globals

MODULE = 'version.py'

VERSION_RESOURCE_PATH = {
    '1.2.10': '/api/v1/archive-config/network-device',
    '1.3.0.2': '/api/v1/archive-config/network-device',
    '1.3.0.3': '/api/v1/archive-config/network-device',
    '1.3.1.3': '/api/v1/archive-config/network-device'
}

VERSION_SUB_RESOURCE_PATH = {
    '1.2.10': '/version',
    '1.3.0.2': '/version',
    '1.3.0.3': '/version',
    '1.3.1.3': '/version'
}

CONFIG_FILE_SUB_RESOURCE_PATH = {
    '1.2.10': '/file',
    '1.3.0.2': '/file',
    '1.3.0.3': '/file',
    '1.3.1.3': '/file'
}

RUNNING_CONFIG = 'RUNNINGCONFIG'
STARTUP_CONFIG = 'STARTUPCONFIG'
VLAN = 'VLAN'

CONFIG_FILE_TYPES = [
    RUNNING_CONFIG,
    STARTUP_CONFIG
]

# error conditions

NO_SYNC = ''
NO_CONFIG = {}

# error messages and resolutions

ILLEGAL_CONFIG_FILE_TYPE = 'Illegal config file type'
VERSION_DELETE_FAILED = 'Version deletion failed'


class Version(DnacApi):
    """
    The Version class represents a configuration archive version created in Cisco DNA Center.  A DeviceArchive wraps
    Version instances, and in turn, ConfigArchive objects wrap DeviceArchives.  It is unnecessary for users to manage
    their own Version instances.
    """
    def __init__(self,
                 dnac,
                 device_id,
                 version_id,
                 verify=False,
                 timeout=5):
        """
        Instantiates a new Version object.
        :param dnac: A reference to the master script's Dnac object.
            type: Dnac object
            required: yes
            default: None
        :param device_id: The UUID for the device whose archive is being managed.
            type: str
            required: yes
            default: none
        :param version_id: The UUID of the version being queried.
            type: str
            required: yes
            default: None
        :param verify: A flag that determines whether or not Cisco DNA Center's certificate should be authenticated.
            type: bool
            required: no
            default: False
        :param timeout: The number of seconds to wait for Cisco DNAC to respond to a query.
            type: int
            required: no
            default: 5
        """
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = '%s/%s%s/%s' % (VERSION_RESOURCE_PATH[dnac.version],
                                  device_id,
                                  VERSION_SUB_RESOURCE_PATH[dnac.version],
                                  version_id)
        else:
            raise DnacError('__init__: %s: %s' % (UNSUPPORTED_DNAC_VERSION, dnac.version))
        self.__id = version_id
        self.__device_id = device_id
        self.__config_files = {}  # key = fileType, value = File object
        name = 'version_%s' % self.__id
        super(Version, self).__init__(dnac,
                                      name,
                                      resource=path,
                                      verify=verify,
                                      timeout=timeout)
        # load the version
        url = self.dnac.url + self.resource
        version, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, '__init__', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], str(version)
                              )
        self.__created_time = version['versions'][0]['createdTime']
        self.__sync_status = version['versions'][0]['startupRunningStatus']
        for file in version['versions'][0]['files']:
            # iterate through all the archive's versions and load the config files
            if file['fileType'] not in CONFIG_FILE_TYPES:
                # ignore VLAN data files
                if file['fileType'] == VLAN:
                    continue
                raise DnacApiError(
                    MODULE, '__init__', ILLEGAL_CONFIG_FILE_TYPE, '',
                    str(CONFIG_FILE_TYPES), '', file['fileType'], ''
                )
            config_file = File(dnac, file['fileId'])
            config_file.get_results(is_json=False)
            self.__config_files[file['fileType']] = config_file

    # end __init__()

    @property
    def id(self):
        """
        The id get method returns the version's UUID.
        :return: str
        """
        return self.__id

    # end id getter

    @property
    def device_id(self):
        """
        Provides the device's UUID being queried.
        :return: str
        """
        return self.__device_id

    # end device_id getter

    @property
    def created_time(self):
        """
        Returns the epoch time the version was created.
        :return: int
        """
        return self.__created_time

    # end created_time getter

    @property
    def sync_status(self):
        """
        Indicates whether or not the device's running config has been sychronized with the startup config for this
        version.
        :return: bool
        """
        return self.__sync_status

    # end sync_status getter

    @property
    def config_files(self):
        """
        Returns the configuration files associated with the Version object.
        :return: dict
        """
        return self.__config_files

    # end config_files getter

    def delete(self):
        """
        Removes the Version object from Cisco DNA Center as well as from the program's Dnac object.
        :return: None
        """
        url = self.dnac.url + self.resource
        results, status = self.crud.delete(url, headers=self.dnac.hdrs)
        if status != OK:
            raise DnacApiError(MODULE, 'delete', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], '')
        task = Task(self.dnac, results['response']['taskId'])
        task.get_task_results()
        if task.is_error:
            raise DnacApiError(MODULE, 'delete', task.progress, '', '', '', task.failure_reason, '')
        else:
            # remove self from Dnac.api{}
            del self.dnac.api[self.name]

    # end delete()

    def delete_config_file(self, file_id):
        """
        Removes the specified file, given by its UUID, from Cisco DNAC and from the Version instance.
        :param file_id: str
        :return: None
        """
        url = '%s%s/%s/%s' % (self.dnac.url, self.resource, CONFIG_FILE_SUB_RESOURCE_PATH[self.dnac.version], file_id)
        results, status = self.crud.delete(url, headers=self.dnac.hdrs)
        if status != OK:
            raise DnacApiError(MODULE, 'delete_config', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], '')
        task = Task(self.dnac, results['response']['taskId'])
        task.get_task_results()
        if task.is_error:
            raise DnacApiError(MODULE, 'delete_config', task.progress, '', '', '', task.failure_reason, '')
        else:
            for config_file_type, config_file in self.__config_files.items():
                if file_id == config_file.id:
                    del self.__config_files[config_file_type]
                    break
            del self.dnac.api['file_%s' % file_id]

    # end delete_config_file

# end class Version

