from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS, \
                      ACCEPTED, \
                      REQUEST_NOT_ACCEPTED
from dnac.version import Version
from dnac.device_archive_task import DeviceArchiveTask
import json

MODULE = 'device_archive.py'

# globals

ARCHIVE_RESOURCE_PATH = {
    '1.2.10': '/api/v1/archive-config',
    '1.3.0.2': '/api/v1/archive-config',
    '1.3.0.3': '/api/v1/archive-config',
    '1.3.1.3': '/api/v1/archive-config',
    '1.3.1.4': '/api/v1/archive-config'
}

DEVICE_ARCHIVE_RESOURCE_PATH = {
    '1.2.10': '%s/network-device' % ARCHIVE_RESOURCE_PATH['1.2.10'],
    '1.3.0.2': '%s/network-device' % ARCHIVE_RESOURCE_PATH['1.3.0.2'],
    '1.3.0.3': '%s/network-device' % ARCHIVE_RESOURCE_PATH['1.3.0.3'],
    '1.3.1.3': '%s/network-device' % ARCHIVE_RESOURCE_PATH['1.3.1.3'],
    '1.3.1.4': '%s/network-device' % ARCHIVE_RESOURCE_PATH['1.3.1.4']
}

# error conditions

NO_ARCHIVED_CONFIGS = []
SINGLE_DEVICE = 1

# error messages and resolutions

ILLEGAL_DEVICE_LIST = 'Illegal device ID list'
LEGAL_DEVICE_LIST = 'dict'
DEVICE_LIST_RESOLUTION = 'Only one device allowed.  Device list is empty or has multiple entries.'
ILLEGAL_DEVICE_TYPE = 'Illegal device type'
LEGAL_DEVICE_TYPE = 'class NetworkDevice'
DEVICE_TYPE_RESOLUTION = 'Create the config archive with a valid NetworkDevice object'
SINGLE_DEVICE_ERROR = 'Archive requested includes multiple devices'
SINGLE_DEVICE_ERROR_RESOLUTION = 'Modify the request\'s scope to one device only.'


class DeviceArchive(DnacApi):
    """
    The DeviceArchive class manages the configuration archive for a device.  It can be used to create new versions
    and delete old ones.

    Usage:
        d = Dnac()
        device = NetworkDevice(d, 'aDevice')
        archive = DeviceArchive(d, device.devices['id'])
        archive.add_configs_to_archive(running=True, startup=True)
        for version in archive.versions:
            for file in version.config_files:
                pprint.PrettyPrinter(file)
            archive.delete_version(version)
    """

    def __init__(self,
                 dnac,
                 device_id,
                 verify=False,
                 timeout=5):
        """
        Creates a new DeviceArchive object and sets the target network device's ID.
        :param dnac: Reference to the program's Dnac object.
            type: Dnac object
            required: yes
            default: None
        :param device_id: The UUID in Cisco DNAC for the device to be managed.
            type: str
            required: yes
            default: None
        :param verify: Flag indicating whether or not to validate Cisco DNA Center's certificate.
            type: bool
            required: no
            default: False
        :param timeout: Number of seconds to wait for Cisco DNA Center to respond to an API call.
            type: int
            required: no
            default: 5
        """
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = DEVICE_ARCHIVE_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError('%s: __init__: %s: %s' % (MODULE, UNSUPPORTED_DNAC_VERSION, dnac.version))
        self.__device = device_id
        self.__versions = []  # list of Version objects that contain the config files
        super(DeviceArchive, self).__init__(dnac,
                                            '%s_archive' % self.__device,
                                            resource=path,
                                            verify=verify,
                                            timeout=timeout)

    # end __init__()

    @property
    def device(self):
        """
        Yields the target devices' UUID.
        :return: str
        """
        return self.__device

    # end device getter

    @property
    def versions(self):
        """
        Provides the list of archive versions available for the device.
        :return: list
        """
        return self.__versions

    # end versions getter

    def load_versions(self):
        """
        Instructs the DeviceArchive instance to load all the device's configs available in Cisco DNAC's archive and
        then return them.
        :return: list
        """
        # make a GET call to DNAC for the latest versions list
        url = '%s%s/%s/version' % (self.dnac.url, self.resource, self.__device)
        versions, status = self.crud.get(url,
                                         headers=self.dnac.hdrs,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'versions', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(versions)
            )
        # construct the object's versions list
        vers = versions['versions']
        if vers != NO_ARCHIVED_CONFIGS:
            for version in vers:
                ver = Version(self.dnac, self.__device, version['id'])
                self.__versions.append(ver)
        return self.__versions

    # end load_versions()

    def delete_version(self, version):
        """
        Deletes the indicated version and its configs from DNA Center's archive.
        :param version: The version to be removed.
            type: Version object
            required: yes
            default: None
        :return: None
        """
        self.__versions.remove(version)
        version.delete()

    # end delete_version()

    def add_configs_to_archive(self,
                               running=False,
                               startup=False):
        """
        Instructs the DeviceArchive instance to add a configuration file to Cisco DNA Center's archive and then
        refresh all available versions.
        :param running: A flag indicating whether or not the device's running config should be archived.
            type: bool
            required: no
            default: False
        :param startup: A flag indicating whether or not the device's startup config should be archived.
            type: bool
            required: no
            default: False
        :return: None
        """
        device_id_list = [self.__device]
        # format the request body
        #   'vlan' and 'all' keys currently cause task failure; default these to False
        requested_configs = {
                             'startupconfig': startup,
                             'runningconfig': running,
                             'vlan': False,
                             'all': False
                            }
        request_body = {
                        'deviceIds': device_id_list,
                        'configFileType': requested_configs
                       }
        body = json.dumps(request_body)
        # issue the request to add configs to the archive
        url = self.dnac.url + ARCHIVE_RESOURCE_PATH[self.dnac.version]
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=body,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, 'add_configs_to_archive', REQUEST_NOT_ACCEPTED, url,
                ACCEPTED, status, ERROR_MSGS[status], str(results)
                              )
        # monitor the task
        device_archive_task = DeviceArchiveTask(self.dnac, results['response']['taskId'])
        device_archive_task.get_task_results()
        # return the object's new versions list
        return self.load_versions()

    # end add_configs_to_archive()

# end class DeviceArchive()

