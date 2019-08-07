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

ARCHIVE_RESOURCE_PATH = {
    '1.2.10': '/api/v1/archive-config',
    '1.3.0.2': '/api/v1/archive-config',
    '1.3.0.3': '/api/v1/archive-config'
}

DEVICE_ARCHIVE_RESOURCE_PATH = {
    '1.2.10': '%s/network-device' % ARCHIVE_RESOURCE_PATH['1.2.10'],
    '1.3.0.2': '%s/network-device' % ARCHIVE_RESOURCE_PATH['1.3.0.2'],
    '1.3.0.3': '%s/network-device' % ARCHIVE_RESOURCE_PATH['1.3.0.3']
}

NO_ARCHIVED_CONFIGS = []
ILLEGAL_DEVICE_LIST = 'Illegal device ID list'
LEGAL_DEVICE_LIST = 'dict'
DEVICE_LIST_RESOLUTION = 'Only one device allowed.  Device list is empty or has multiple entries.'
ILLEGAL_DEVICE_TYPE = 'Illegal device type'
LEGAL_DEVICE_TYPE = 'class NetworkDevice'
DEVICE_TYPE_RESOLUTION = 'Create the config archive with a valid NetworkDevice object'
SINGLE_DEVICE = 1
SINGLE_DEVICE_ERROR = 'Archive requested includes multiple devices'
SINGLE_DEVICE_ERROR_RESOLUTION = 'Modify the request\'s scope to one device only.'


class DeviceArchive(DnacApi):

    def __init__(self,
                 dnac,
                 device_id,
                 verify=False,
                 timeout=5):

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
        return self.__device

# end device getter

    @property
    def versions(self):
        return self.__versions

# end versions getter

    def load_versions(self):
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

    def add_configs_to_archive(self,
                               running=False,
                               startup=False):
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

# end class DeviceArchive()

# begin unit test


if __name__ == '__main__':

    from dnac import Dnac
    from dnac.timestamp import TimeStamp

    d = Dnac()
    da = DeviceArchive(d, '84e4b133-2668-4705-8163-5694c84e78fb')

    print('DeviceArchive:')
    print()
    print('  name     = ', da.name)
    print('  device   = ', da.device)
    print('  versions = ', str(da.versions))
    print()

    print()
    print('  name     = ', da.name)
    print('  device   = ', da.device)
    print('  versions = ', str(da.versions))
    print()

    print('DeviceArchive: adding current configs to archive:')

    da.add_configs_to_archive(running=True, startup=True)

    print()
    print('  name     = ', da.name)
    print('  device   = ', da.device)
    print('  versions = ', str(da.versions))
    print()
    print('DeviceArchive: printing the archive:')
    print()

    for version in da.versions:
        print('  name    = ', version.name)
        print('  device   = ', da.device)
        print('  version = ', version.id)
        t = TimeStamp(version.created_time)
        print('  created time = ', t.local_timestamp())
        print('  sync status  = ', version.sync_status)
        keys = version.config_files.keys()
        for key in keys:
            print('  config file type = ', key)
            print('  contents = ')
            print(version.config_files[key].results)
            print()
            print()
