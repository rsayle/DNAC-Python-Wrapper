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
from dnac.device_archive import DeviceArchive

MODULE = 'config_archive.py'

ARCHIVE_RESOURCE_PATH = {
    '1.2.10': '/api/v1/archive-config',
    '1.3.0.2': '/api/v1/archive-config',
    '1.3.0.3': '/api/v1/archive-config'
}

ARCHIVE_ALREADY_EXISTS_ERROR = 'A device archive already exists for the requested host'

class ConfigArchive(DnacApi):

    def __init__(self,
                 dnac,
                 name,
                 verify=False,
                 timeout=5):

        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = ARCHIVE_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError('%s: __init__: %s: %s' % (MODULE, UNSUPPORTED_DNAC_VERSION, dnac.version))
        self.__archive = {}  # key = deviceId, value = DeviceArchive
        super(ConfigArchive, self).__init__(dnac,
                                            '%s_archive' % name,
                                            resource=path,
                                            verify=verify,
                                            timeout=timeout)

# end __init__()

    @property
    def archive(self):
        return self.__archive

# end archive getter

    def load_all_archives(self):
        url = self.dnac.url + self.resource
        archives, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'load_all_archives', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(archives)
            )
        for archive in archives['archiveResultlist']:
            device_archive = DeviceArchive(self.dnac, archive['deviceId'])
            device_archive.load_versions()
            self.__archive[archive['deviceId']] = device_archive
        return self.__archive

# end load_all_archives()

    def load_device_archive(self, device):
        if device in self.__archive.keys():
            del self.__archive[device]
        device_archive = DeviceArchive(d, device)
        device_archive.load_versions()
        self.__archive[device] = device_archive
        return self.__archive

# end load_device_archive

    def add_new_archive(self, device):
        if device in self.__archive.keys():
            raise DnacApiError(MODULE, 'add_new_device_archive', ARCHIVE_ALREADY_EXISTS_ERROR, '',
                               '', device, '', '')
        new_archive = DeviceArchive(self.dnac, device)
        self.__archive[device] = new_archive
        return new_archive


# end class ConfigArchive()


if __name__ == '__main__':

    from dnac import Dnac
    from dnac.networkdevice import NetworkDevice
    from dnac.timestamp import TimeStamp

    d = Dnac()
    nd = NetworkDevice(d, 'device')
    ts = TimeStamp()
    ca = ConfigArchive(d, d.name)

    print('ConfigArchive:')
    print()
    print('  archive      = ', ca.archive)
    print('  len(archive) = %i' % len(ca.archive))
    print()

    print('ConfigArchive: load all archives:')
    print()

    ca.load_all_archives()

    print()
    print('  archive      = ', ca.archive)
    print('  len(archive) = %i' % len(ca.archive))
    print()

    print('Config Archive: archive contents :')
    for device in ca.archive:
        print()
        device_archive = ca.archive[device]
        print('  name     = ', device_archive.name)
        print('  device   = ', device_archive.device)
        nd.get_device_by_id(device_archive.device)
        print('  hostname = ', nd.devices['hostname'])
        print('  versions = ', len(device_archive.versions))
        for version in device_archive.versions:
            print()
            print('    id           = ', version.id)
            ts.timestamp = version.created_time
            print('    created time = ', ts.local_timestamp())
            print('    files        = %i' % len(version.config_files))
            print('    config types = ')
            for key in version.config_files.keys():
                print('      ', key)
    print()

    print('ConfigArchive: loading archive for 84e4b133-2668-4705-8163-5694c84e78fb')
    print()

    ca.load_device_archive('84e4b133-2668-4705-8163-5694c84e78fb')

    print()
    print('  archive      = ', ca.archive)
    print('  len(archive) = %i' % len(ca.archive))
    print()

    print('Config Archive: archive contents for 84e4b133-2668-4705-8163-5694c84e78fb:')
    for device in ca.archive:
        print()
        device_archive = ca.archive[device]
        print('  name     = ', device_archive.name)
        print('  device   = ', device_archive.device)
        nd.get_device_by_id(device_archive.device)
        print('  hostname = ', nd.devices['hostname'])
        print('  versions = ', len(device_archive.versions))
        for version in device_archive.versions:
            print()
            print('    id           = ', version.id)
            ts.timestamp = version.created_time
            print('    created time = ', ts.local_timestamp())
            print('    files        = %i' % len(version.config_files))
            print('    config types = ')
            for key in version.config_files.keys():
                print('      ', key)
    print()

    print('ConfigArchive: unit test completed')
