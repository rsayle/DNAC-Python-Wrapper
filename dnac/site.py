
from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS
from dnac.timestamp import TimeStamp

# globals

MODULE = 'site.py'

SITE_HEALTH_RESOURCE_PATH = {
    '1.2.10': '/dna/intent/api/v1/site-health'
}

NO_SITES = {}
NO_SITE_HEALTH = {}

# error messages
SITE_NOT_FOUND = 'Unable to find requested site'
SITE_NOT_FOUND_RESOLUTION = 'Check the site\'s name in Design -> Network Hierarchy'

class Site(DnacApi):
    """
    A Site class maps to the objects created in Cisco DNA Center's design site hierarchy.  This class allows
    developers to pull site health details and assign devices to sites.

    Attributes:
        dnac: A reference to the Dnac instance that contains a Client object
            type: Dnac object
            default: none
            scope: protected
        name: A user friendly name for the Client object used as a key for finding it in a Dnac.api attribute.
            type: str
            default: none
            scope: protected
        sites: A dictionary containing sites matching a site name search.
            type: dict
            default: {}
            scope: protected
        site_health: The health details for each site.
            type: dict
            default: {}
            scope: protected
        verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: no
        timeout: The number of seconds to wait for Cisco DNAC's
                 response.
            type: int
            default: 5
            required: no

    Usage:
        d = Dnac()
        all_sites = Site(d, 'sites')
    """

    def __init__(self,
                 dnac,
                 name,
                 site=NO_SITES,
                 verify=False,
                 timeout=5):

        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = SITE_HEALTH_RESOURCE_PATH[dnac.version]  # change when a site resource becomes available
            self.__site_health_resource = SITE_HEALTH_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError(
                '__init__: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                           )
        self.__sites = site
        self.__site_health = NO_SITE_HEALTH
        super(Site, self).__init__(dnac,
                                   name,
                                   resource=path,
                                   verify=verify,
                                   timeout=timeout)

# end __init__()

    @property
    def sites(self):
        """
        The sites getter method returns the current value of the Site class' sites attribute.

        Paramters:
            None

        Return Values:
            dict: All sites in Cisco DNAC's site design hierarchy

        Usage:
            d = Dnac()
            all_sites = Site(d, 'ACME_sites')
            pprint.PrettyPrint(d.api['ACME_sites'].sites)
        """
        return self.__sites

# end sites getter

    @property
    def site_health(self):
        """
        The site_health getter method returns the current value of each site's health in Cisco DNAC.

        Paramters:
            None

        Return Values:
            dict: site health state for each site.

        Usage:
            d = Dnac()
            all_sites = Site(d, 'ACME_sites')
            pprint.PrettyPrint(d.api['ACME_sites'].site_health)
        """
        return self.__site_health

# end site_health getter

    def get_all_sites_health(self):
        """
        Site class method get_all_sites_health retrieves the current health details for all sites in
        Cisco DNA Center.

        Parameters:
            None

        Return Values:
            dict: The health details for all sites.

        Usage:
            d = Dnac()
            all_sites = Site(d, 'ACME_sites')
            pprint.PrettyPrint(d.api['ACME_sites'].get_all_sites_health())
        """
        time = TimeStamp()
        query = '?timestamp=%s' % time
        url = self.dnac.url + self.resource + query
        health, status = self.crud.get(url,
                                       headers=self.dnac.hdrs,
                                       verify=self.verify,
                                       timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_all_sites_health', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(health)
            )
        self.__site_health = health['response']
        return self.__site_health

# end get_all_sites_health()

    def get_site_health_by_name(self, site_name):
        """
        The get_site_health_by_name returns the site health information for the named site.

        Parameters:
            site_name: The target site's name
                type: str
                default: none
                required: yes

        Return Values:
            dict: The site's health details.

        Usage:
            d = Dnac()
            all_sites = Site(d, 'ACME_sites')
            target_site = 'AZ Branch'
            pprint.PrettyPrint(d.api['ACME_sites'].get_site_health_by_name(target_site))
        """
        target_site_health = NO_SITE_HEALTH
        all_sites_health = self.get_all_sites_health()
        for site_health in all_sites_health:
            if site_health['siteName'] == site_name:
                target_site_health = site_health
                break  # found the target site
            else:
                continue  # keep searching
        if target_site_health == NO_SITE_HEALTH:  # site not found
            raise DnacApiError(
                MODULE, 'get_all_sites_health', SITE_NOT_FOUND, '',
                site_name, '', '', SITE_NOT_FOUND_RESOLUTION
            )
        self.__site_health = target_site_health
        return self.__site_health

# end get_site_health_by_name

# end class Site()

# begin unit test


if __name__ == '__main__':
    from dnac import Dnac
    import pprint

    pp = pprint.PrettyPrinter(indent=4)
    d = Dnac()
    s = Site(d, 'aSite')

    print('Site:')
    print()
    print('Getting the health of all sites...')
    print()

    s.get_all_sites_health()

    pp.pprint(s.site_health)

    print()
    print('Getting site health for Denver Office...')

    s.get_site_health_by_name('Denver Office')

    pp.pprint(s.site_health)

    print()
    print('Testing exceptions...')

    try:
        s.get_site_health_by_name('No Such Site')
    except DnacApiError as e:
        print(str(type(e)) + " = " + str(e))

    print()
    print('Site: end unit test')
    print()
