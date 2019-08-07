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
    '1.3.0.3': '/api/v1/archive-config/setting'
}

SUCCESSFUL_ARCHIVE_SETTINGS_UPDATE = 'SUCCESS'


class ConfigArchiveSettings(DnacApi):

    def __init__(self,
                 dnac,
                 name,
                 verify=False,
                 timeout=5):
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
        self.__settings = settings
        #new_settings = {'timeout': self.__settings['timeout'],
        #                'noOfDays': self.__settings['noOfDays'],
        #                'noOfVersion': self.__settings['noOfVersion']}
        #new_settings = json.dumps(new_settings)
        # make a PUT call to DNAC for the new settings
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

# begin unit test

if __name__ == '__main__':

    from dnac import Dnac

    d = Dnac()
    a = ConfigArchiveSettings(d, d.name)

    print('ConfigArchiveSettings:')
    print()
    print('  name =     ', a.name)
    print('  settings = ', a.settings)
    print()

    print('ConfigArchive: changing archive settings:')
    print()

    new = {'timeout': 360001, 'noOfDays': 30, 'noOfVersion': 10}
    a.settings = new

    print()
    print('  name =     ', a.name)
    print('  settings = ', a.settings)
    print()
    print('ConfigArchiveSettings: unit test complete.')