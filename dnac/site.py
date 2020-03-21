
from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS, \
                      _500_
from dnac.timestamp import TimeStamp
import json

# globals

MODULE = 'site.py'


SITE_RESOURCE_PATH = {
    '1.2.10': '/dna/intent/api/v1/site',
    '1.3.0.2': '/dna/intent/api/v1/site',
    '1.3.0.3': '/dna/intent/api/v1/site',
    '1.3.1.3': '/dna/intent/api/v1/site',
    '1.3.1.4': '/dna/intent/api/v1/site'
}

SITE_HEALTH_RESOURCE_PATH = {
    '1.2.10': '/dna/intent/api/v1/site-health',
    '1.3.0.2': '/dna/intent/api/v1/site-health',
    '1.3.0.3': '/dna/intent/api/v1/site-health',
    '1.3.1.3': '/dna/intent/api/v1/site-health',
    '1.3.1.4': '/dna/intent/api/v1/site-health'
}

STUB_SITE = 'STUB_SITE'
LOCATION = 'Location'
MAPS_SUMMARY = 'mapsSummary'
MAP_GEOMETRY = 'mapGeometry'
AREA = 'area'
BUILDING = 'building'
FLOOR = 'floor'
CUBES_AND_WALLED_OFFICES = 'Cubes and Walled Offices'
DRYWALL_OFFICE_ONLY = 'Drywall Office Only'
INDOOR_HIGH_CEILING = 'Indoor High Ceiling'
OUTDOOR_OPEN_SPACE = 'Outdoor Open Space'

VALID_SITE_TYPES = [AREA, BUILDING, FLOOR]
VALID_RF_MODELS = [CUBES_AND_WALLED_OFFICES, DRYWALL_OFFICE_ONLY, INDOOR_HIGH_CEILING, OUTDOOR_OPEN_SPACE]

RF_MODELS = {
    '54054': CUBES_AND_WALLED_OFFICES,
    '54055': DRYWALL_OFFICE_ONLY,
    '54056': OUTDOOR_OPEN_SPACE,
    '54057': INDOOR_HIGH_CEILING
}

# error conditions

NO_SITE = {}
NO_SITE_HEALTH = {}
SINGLE_SITE = 1
INVALID_SITE_TYPE_ERROR = 'Illegal site type'
INVALID_RF_MODEL_ERROR = 'Illegal RF model'

# error and resolution messages
SITE_NOT_FOUND = 'Unable to find requested site'
SITE_NOT_FOUND_RESOLUTION = 'Check the site\'s name in Design -> Network Hierarchy'
MULTIPLE_SITES_FOUND = 'Found multiple sites when only one was expected'
VALID_SITE_TYPES_RESOLUTION = 'Valid site types include %s' % str(VALID_SITE_TYPES)
VALID_RF_MODELS_RESOLUTION = 'Valid RF models include %s' % str(VALID_RF_MODELS)

class Site(DnacApi):
    """
    A Site class maps to the objects created in Cisco DNA Center's design site hierarchy.  This class allows
    developers to pull a site's information and its health.  It also allows creation of new sites.

    To create new sites in a cluster, instantiate a stub site by calling for a new Site object whose name is
    STUB_SITE: stub_site = Site(dnac, STUB_SITE).

    Attributes:
        dnac: A reference to the Dnac instance that contains a Client object
            type: Dnac object
            default: none
            scope: protected
        name: A user friendly name for the Client object used as a key for finding it in a Dnac.api attribute.
              For Site objects, use the site's fully qualified hierarchy name, e.g. Global/US/California/Irvine
            type: str
            default: none
            scope: protected
        site: A dictionary containing the site's information.
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
        irvine = Site(d, 'Global/US/California/Irvine')
    """

    def __init__(self,
                 dnac,
                 site_name_hierarchy,  # use the site's name hierarchy to ensure uniqueness
                 verify=False,
                 timeout=5):
        """
        Creates a new Site object and loads its information from the Cisco DNA Center cluster specified.
        :param dnac: The Cisco DNAC cluster object from which to load the site's information.
            type: Dnac object
            required: yes
            default: none
        :param site_name_hierarchy: The site's full hierarchy name as given in Cisco DNA Center, e.g. Global/US/CA
            type: str
            required: yes
            default: none
        :param verify: A flag indicating whether or not to verify the cluster's certificate.
            type: bool
            required: no
            default: False
        :param timeout: The number of seconds to wait for a site API call to complete before abandoning the response.
            type: int
            required: no
            default: 5
        """
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = SITE_RESOURCE_PATH[dnac.version]
            self.__site_health_resource = SITE_HEALTH_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError('__init__: %s: %s' % (UNSUPPORTED_DNAC_VERSION, dnac.version))
        self.__site = NO_SITE
        self.__site_health = NO_SITE_HEALTH
        super(Site, self).__init__(dnac,
                                   site_name_hierarchy,
                                   resource=path,
                                   verify=verify,
                                   timeout=timeout)
        if site_name_hierarchy != STUB_SITE:
            self.load_site(site_name_hierarchy)

    # end __init__()

    @property
    def site(self):
        """
        Provides the site's details as returned from Cisco DNA Center.
        :return: dict
        """
        return self.__site

    # end site getter

    @property
    def name(self):
        """
        Yields the site's name.
        :return: str
        """
        return self.__site['name']

    # end name getter

    @property
    def site_name_hierarchy(self):
        """
        Getter method that furnishes the site's fully qualified site hierarchy.
        :return: str
        """
        return self.__site['siteNameHierarchy']

    # end site_name_hierarchy getter

    @property
    def id(self):
        """
        Returns the site's UUID.
        :return: str
        """
        return self.__site['id']

    # end id getter

    @property
    def parent_id(self):
        """
        Provides the site's parent site UUID.
        :return: str
        """
        return self.__site['parentId']

    # end parent_id getter

    @property
    def parent_name(self):
        """
        Parses the site's hierarchy name and returns its parent site's hierarchy name.
        :return: str
        """
        name_hierarchy = self.__site['siteNameHierarchy'].split('/')
        name_hierarchy.pop()
        return '/'.join(name_hierarchy)

    @property
    def location(self):
        """
        Finds the location name space in the site's additional information and returns the location's attributes.
        :return: dict
        """
        for info in self.__site['additionalInfo']:
            if info['nameSpace'] == LOCATION:
                return info['attributes']

    # end location getter

    @property
    def address(self):
        """
        Returns a building's address.
        :return: str
        """
        return self.location['address']

    # end address getter

    @property
    def latitude(self):
        """
        Returns the building's latitudinal location.
        :return: str
        """
        return self.location['latitude']

    # end latitude getter

    @property
    def longitude(self):
        """
        Returns the building's longitudinal location.
        :return: str
        """
        return self.location['longitude']

    # end longitude

    @property
    def maps_summary(self):
        """
        Finds the floors's map information.
        :return: dict
        """
        for info in self.__site['additionalInfo']:
            if info['nameSpace'] == MAPS_SUMMARY:
                return info['attributes']

    # end maps_summary getter

    @property
    def rf_model(self):
        """
        Returns the floors's assigned RF model.  Valid models are listed in the VALID_RF_MODELS list.  This method uses
        the RF_MODELS map to return the values in the VALID_RF_MODELS list.  Cisco DNAC stores the models as a number
        but requires users to specify them as strings, hence, the RF_MODELS map.
        :return: str
        """
        return RF_MODELS[self.maps_summary['rfModel']]

    # end rf_model getter

    @property
    def map_geometry(self):
        """
        Furnishes the floor's map geometry, e.g. length, width, height.
        :return: dict
        """
        for info in self.__site['additionalInfo']:
            if info['nameSpace'] == MAP_GEOMETRY:
                return info['attributes']

    # end map_geometry getter

    @property
    def length(self):
        """
        Returns a floor's map length.
        :return: str
        """
        return self.map_geometry['length']

    # end length getter

    @property
    def width(self):
        """
        Returns a floor's map width.
        :return: str
        """
        return self.map_geometry['width']

    # end width getter

    @property
    def height(self):
        """
        Returns a floor's map height.
        :return: str
        """
        return self.map_geometry['height']

    # end height getter

    @property
    def site_health(self):
        """
        Return's a site's health information.
        :return: dict
        """
        return self.__site_health

    # end site_health getter

    def load_site(self, site_name_hierarchy):
        """
        Using the site's fully qualified hierarchy name, this method queries the Cisco DNA center cluster for the
        site's information and loads it into it's __site attribute.
        :param site_name_hierarchy: The site's fully qualifies site name, e.g. Global/EU/England/London
        :return: dict
        """
        filter = '?name=%s' % site_name_hierarchy
        url = '%s%s%s' % (self.dnac.url, self.resource, filter)
        site, status = self.crud.get(url,
                                     headers=self.dnac.hdrs,
                                     verify=self.verify,
                                     timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'load_site', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], site_name_hierarchy
            )
        if len(site['response']) != SINGLE_SITE:
            raise DnacApiError(
                MODULE, 'load_site', MULTIPLE_SITES_FOUND, '', SINGLE_SITE, len(site['response']), '', ''
            )
        self.__site = site['response'][0]
        return self.__site

    # end load_site

    def __make_area_body__(self, name, parent_name_hierarchy):
        """
        A hidden method used by a Site object to prepare the parameters needed to create a new area in the cluster.
        :param name: The area's name.
            type: str
            required: yes
            default: none
        :param parent_name_hierarchy: The area's parent's fully qualified site name hierarchy.
            type: str
            required: yes
            default: none
        :return: JSON formatted str
        """
        area = {'name': name, 'parentName': parent_name_hierarchy}
        site = {'area': area}
        body = {'type': AREA, 'site': site}
        return json.dumps(body)

    # end __make_area_body__()

    def __make_building_body__(self, name, parent_name_hierarchy, latitude, longitude, address=None):
        """
        A hidden method used by a Site object to prepare the parameters need to create a new building.
        :param name: The building's name.
            type: str
            required: yes
            default: none
        :param parent_name_hierarchy: The building's parent's fully qualified site hierarchy name.
            type: str
            required: yes
            default: none
        :param latitude: The building's latitudinal location.
            type: str
            required: yes
            default: none
        :param longitude: The building's longitudinal location.
            type: str
            required: yes
            default: none
        :param address: The building's physical address.
            type: str
            required: no
            default: none
        :return: JSON formatted str
        """
        building = {'name': name, 'parentName': parent_name_hierarchy,
                    'latitude': latitude, 'longitude': longitude}
        if bool(address):
            building['address'] = address
        site = {'building': building}
        body = {'type': BUILDING, 'site': site}
        return json.dumps(body)

    # end __make_building_body()

    def __make_floor_body__(self, name, parent_name_hierarchy, rf_model, width, length, height):
        """
        A hidden method used by a Site object to prepare the parameters necessary to create a new floor.
        :param name: The floor's name.
            type: str
            required: yes
            default: none
        :param parent_name_hierarchy: The floor's parent's fully qualified site name hierarchy.
            type: str
            required: yes
            default: none
        :param rf_model: The RF model used to calculate the floor's wireless coverage.
            type: str from VALID_RF_MODELS
            required: yes
            default: none
        :param width: The floor's width in feet.
            type: str
            required: yes
            default: none
        :param length: The floor's length in feet.
            type: str
            required: yes
            default: none
        :param height: The floor's height in feet.
            type: str
            required: yes
            default: none
        :return: JSON formatted str
        """
        floor = {'name': name, 'parentName': parent_name_hierarchy, 'rfModel': rf_model, 'width': width,
                 'length': length, 'height': height}
        site = {'floor': floor}
        body = {'type': FLOOR, 'site': site}
        return json.dumps(body)

    # end __make_floor_body__()

    def add_site(self, site_type, name, parent_name_hierarchy, address=None, latitude=None, longitude=None,
                 rf_model=None, width=None, length=None, height=None):
        """
        Makes a call to Cisco DNA Center to create a new site.
        :param site_type: The type of site to create: area, building, or floor.
            type: str from VALID_SITE_TYPES
            required: yes
            default: none
        :param name: The site's name, e.g. Irvine.
            type: str
            required: yes
            default: none
        :param parent_name_hierarchy: The site's parent's fully qualified hierarchy name, e.g. Global/US/California
            type: str
            required: yes
            default: none
        :param address: A building's physical address, e.g. 130 Theory Drive, Irvine, CA, 92617
            type: str
            required: no, but only be used if the site type is a building.  Does not apply to any other site types.
            default: none
        :param latitude: A building's latitudinal location.
            type: str
            required: Mandatory if the site type is a building.  Does not apply to any other site types.
            default: none
        :param longitude: A building's longitudinal location.
            type: str
            required: Mandatory if the site type is a building.  Does not apply to any other site types.
            default: none
        :param rf_model: The RF model used to calculate a floor's heat map.
            type: str from VALID_RF_MODELS
            required: Mandatory if the site type is a floor.  Does not apply to any other site types.
            default: none
        :param width: A floor's width in feet.
            type: str
            required: mandatory if the site type is a floor.  Does not apply to any other site types.
        :param length: A floor's length in feet.
            type: str
            required: mandatory if the site type is a floor.  Does not apply to any other site types.
        :param height: A floor's height in feet.
            type: str
            required: mandatory if the site type is a floor.  Does not apply to any other site types.
        :return: Site object
        """
        if site_type == AREA:
            body = self.__make_area_body__(name, parent_name_hierarchy)
        elif site_type == BUILDING:
            body = self.__make_building_body__(name, parent_name_hierarchy, latitude, longitude, address)
        elif site_type == FLOOR:
            body = self.__make_floor_body__(name, parent_name_hierarchy, rf_model, width, length, height)
        else:
            raise DnacApiError(
                MODULE, 'add_site', INVALID_SITE_TYPE_ERROR, '', '', site_type, '', VALID_SITE_TYPES_RESOLUTION
            )
        headers = {'__runsync': 'true'}
        headers.update(self.dnac.hdrs)
        url = '%s%s' % (self.dnac.url, self.resource)
        results, status = self.crud.post(url,
                                         headers=headers,
                                         body=body,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != OK:
            if status == _500_:
                raise DnacApiError(
                    MODULE, 'add_site', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], results['FailureReason']
                )
            else:
                raise DnacApiError(
                    MODULE, 'add_site', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], json.dumps(results)
                )
        # use the newly created site's siteId to get its site hierarchy name so a new Site object can be created
        filter = '?siteId=%s' % results['siteId']
        url = '%s%s%s' % (self.dnac.url, self.resource, filter)
        results, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'add_site', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], json.dumps(results)
            )
        return Site(self.dnac, results['response']['siteNameHierarchy'])

    # end add_site()

    def get_all_sites_health(self):
        """
        Returns the site health information for every site.
        :return: dict
        """
        time = TimeStamp()
        query = '?timestamp=%s' % time
        url = '%s%s%s' % (self.dnac.url, self.resource, query)
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
        Gives the named site's health.
        :param site_name: The site's name.
            type: str
            required: yes
            default: none
        :return: dict
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

