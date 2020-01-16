from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS
from dnac.device_archive import DeviceArchive

MODULE = 'config_archive.py'

ARCHIVE_RESOURCE_PATH = {
    '1.2.10': '/api/v1/archive-config',
    '1.3.0.2': '/api/v1/archive-config',
    '1.3.0.3': '/api/v1/archive-config',
    '1.3.1.3': '/api/v1/archive-config',
    '1.3.1.4': '/api/v1/archive-config'
}

# globals

ARCHIVE_ALREADY_EXISTS_ERROR = 'A device archive already exists for the requested host'


class ConfigArchive(DnacApi):
    """
    The ConfigArchive class represents the device configuration archive in Cisco DNA Center.  For any given Cisco DNAC
    cluster, there is one and only one configuration archive.  For this implementation, ConfigArchive is a container
    that holds a set of DeviceArchive objects.

    Attributes:
        dnac: A pointer to the Dnac object containing the ConfigArchive instance.
            type: Dnac object
            default: none
            scope: protected
        name: A user-friendly name for accessing the ConfigArchive object in a Dnac.api{}.
            type: str
            default: none
            scope: protected
        archive: a dict that holds DeviceArchive instances.  Use a device's UUID as the key to access it's
                 associated DeviceArchive.
            type: dict
            default: {}
            scope: protected
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
        dnac_archive = ConfigArchive(d, 'archive')
        dnac_archive.load_all_archives()
    """

    def __init__(self,
                 dnac,
                 name,
                 verify=False,
                 timeout=5):
        """
        ConfigArchive's __init__ method initializes the object with an empty archive.

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: none
                required: yes
            name: A user friendly name for finding this object in a Dnac
                  instance.
                type: str
                default: none
                required: yes
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
            ConfigArchive object: The newly constructed ConfigArchive

        Usage:
            d = Dnac()
            dnac_archive = ConfigArchive(d, 'archive')
        """

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
        """
        Get method archive returns the __archive dictionary.

        Parameters:
            None

        Return Values:
            dict: The DeviceArchives keyed by a device's UUID.

        Usage:
            d = Dnac()
            dnac_archive = ConfigArchive(d, 'archive')
            dnac_archive.load_all_archives()
            a_device_archive = dnac_archive.archive[<a_device_uuid>]
        """
        return self.__archive

    # end archive getter

    def load_all_archives(self):
        """
        ConfigArchive uses its load_all_archives method to retrieve the entire configuration archive from a Cisco
        DNA Center cluster.

        Parameters:
            None

        Return Values:
            dict: the device archive

        Usage:
            d = Dnac()
            dnac_archive = ConfigArchive(d, 'archive')
            dnac_archive.load_all_archives()
        """
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
        """
        The load_device_archive instructs a ConfigArchive to pull the configuration archive of a single device.
        If the archive already contains the device's config, ConfigArchive first deletes the existing archive and
        then it reloads the information from Cisco DNA Center.

        Parameters:
            device: the target device's UUID
                type: str
                default: none
                required: yes

        Return Values:
            dict: reference to the newly loaded device archive

        Usage:
            d = Dnac()
            device = NetworkDevice(d, 'device')
            dnac_archive = ConfigArchive(d, 'archive')
            device_archive = dnac_archive.load_device_archive(device.get_device_by_name('aHostName')['id'])
        """
        if device in self.__archive.keys():
            del self.__archive[device]
        device_archive = DeviceArchive(d, device)
        device_archive.load_versions()
        self.__archive[device] = device_archive
        return self.__archive[device]

    # end load_device_archive

    def add_new_archive(self, device):
        """
        The add_new_archive method creates a new DeviceArchive from a device's UUID and then stores it in the
        ConfigArchive's archive attribute.

        Parameters:
            device: A device's UUID
                type: str
                default: none
                required: yes

        Return Values:
            A new DeviceArchive object

        Usage:
            d = Dnac()
            device = NetworkDevice(d, 'device')
            dnac_archive = ConfigArchive(d, 'archive')
            device_archive = dnac_archive.add_new_device_archive(device.get_device_by_name('aHostName')['id'])
        """
        if device in self.__archive.keys():
            raise DnacApiError(MODULE, 'add_new_device_archive', ARCHIVE_ALREADY_EXISTS_ERROR, '',
                               '', device, '', '')
        new_archive = DeviceArchive(self.dnac, device)
        self.__archive[device] = new_archive
        return new_archive

    # end add_new_device_archive()

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
