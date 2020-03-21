
from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION, \
                 NO_DNAC_PATH, \
                 NO_DNAC_PATH_ERROR, \
                 NO_DNAC_PATH_RESOLUTION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS
from dnac.site import Site, \
                      SITE_RESOURCE_PATH
from multi_key_dict import multi_key_dict

MODULE = 'site_hierarchy.py'

SITE_COUNT_RESOURCE_PATH = {
    '1.2.10': '/count',
    '1.3.0.2': '/count',
    '1.3.0.3': '/count',
    '1.3.1.3': '/count',
    '1.3.1.4': '/count'
}


SITE_HIERARCHY_NAME = '_site_hierarchy'  # suffix used to differentiate between cluster hierarchies
GLOBAL_SITE = 'Global'
SITE_REQUEST_LIMIT = 500  # only a maximum of 500 site records may be retrieved at any give time
SITE_API_THROTTLE = 1000  # DNAC throttles the site API to 1000 requests/min

NO_GLOBAL_SITE_ERROR = 'Could not find the Global site'
NO_CHILD = []
NO_CHILDREN = []
NO_SITES = 0
NO_SITES_ERROR = 'Could not find any sites in the DNAC cluster'
SITE_ALREADY_EXISTS_ERROR = 'Dnac already contains the site'


class SiteHierarchy(DnacApi):
    """
    The SiteHierarchy class stores each site in a multi-keyed dictionary.  For each site, Cisco DNA Center provides
    the site's parent but not its children.  A SiteHierarchy object stores a site's information and includes a list
    of each site's children so that a hierarchy can be searched by either its parents or its children.  The
    SiteHierarchy stores SiteNodes and uses two keys for each Site: the site's siteHierarchyName and its UUID.  Each
    SiteNode references the site's children.

    Attributes:
        dnac: A pointer to the site hierarchy's Cisco DNAC cluster.
            type: Dnac object
            default: none
            scope: protected
        name: A user friendly name for the Client object used as a key for finding it in a Dnac.api attribute.
              The SiteHierarchy class uses the Dnac object's identifier, i.e. its name or its IP address, and combines
              it with SITE_HIERARCHY_NAME to form the SiteHierarchy object's name for storage in the Dnac object's
              API dictionary.
            type: str
            default: Dnac.name or Dnac.ip + SITE_HIERARCHY_NAME
            scope: public
        all_sites: The Cisco DNA Center information on all sites.
            type: list
            default: []
            scope: protected
        site_nodes: A multi-keyed dictionary of SiteNode objects pointing to all of the cluster's sites.
            type: multi_key_dict
            default: An empty multi_key_dict
            scope: protected
        site_count: The number of sites in the Cisco DNAC cluster.
            type: int
            default: 0
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
        hierarchy = SiteHierarchy(d)
    """

    def __init__(self,
                 dnac,
                 name=SITE_HIERARCHY_NAME,
                 verify=False,
                 timeout=5):
        """
        Creates at new Site object.
        :param dnac: The Cisco DNA Center cluster to which the site belongs.
            type: Dnac object
            required: yes
            default: none
        :param name: The site hierarchy's name.
            type: str
            required: no
            default: Either the Dnac object's name or IP address concatenated with SITE_HIERARCHY_NAME.
        :param verify: A flag indicating whether or not to validate the cluster's certificate.
            type: bool
            required: no
            default: False
        :param timeout: The number of seconds to wait for a response from a site hierarchy API call.
            type: int
            required: no
            default: 5
        """
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = SITE_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError('__init__: %s: %s' % (UNSUPPORTED_DNAC_VERSION, dnac.version))
        if dnac.name != NO_DNAC_PATH:
            site_hierarchy_name = '%s%s' % (dnac.name, name)
        elif dnac.ip != NO_DNAC_PATH:
            site_hierarchy_name = '%s%s' % (dnac.ip, name)
        else:
            raise DnacError('__init__: critical error: %s: %s' % (NO_DNAC_PATH_ERROR, NO_DNAC_PATH_RESOLUTION))
        super(SiteHierarchy, self).__init__(dnac,
                                            site_hierarchy_name,
                                            resource=path,
                                            verify=verify,
                                            timeout=timeout)
        self.__all_sites = []
        self.__site_nodes = multi_key_dict()
        self.__site_count = NO_SITES
        self.load_sites()

    @property
    def all_sites(self):
        """
        Provides the information on all sites.
        :return: dict
        """
        return self.__all_sites

    @property
    def site_nodes(self):
        """
        Returns all SiteNode objects loaded into the SiteHierarchy.
        :return: list of SiteNodes
        """
        return self.__site_nodes

    @property
    def site_count(self):
        """
        Yields the total number of sites loaded into the hierarchy.
        :return: int
        """
        return self.__site_count

    def get_site_count(self):
        """
        Makes a call to the Cisco DNA Center cluster requesting the total number of sites available.
        :return: int
        """
        # get the number of sites in the hierarchy
        if self.dnac.version in SUPPORTED_DNAC_VERSIONS:
            count_path = SITE_COUNT_RESOURCE_PATH[self.dnac.version]
        else:
            raise DnacError('__init__: %s: %s' % (UNSUPPORTED_DNAC_VERSION, self.dnac.version))
        url = '%s%s%s' % (self.dnac.url, self.resource, count_path)
        response, status = self.crud.get(url,
                                         headers=self.dnac.hdrs,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != OK:
            raise DnacApiError(MODULE, 'get_site_count', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], '')
        self.__site_count = response['response']
        if self.__site_count <= NO_SITES:
            raise DnacApiError(MODULE, 'get_site_count', NO_SITES_ERROR, '', '', '', '', '')
        return self.__site_count

    def get_all_sites(self):
        """
        Places an API call to the hierarchy's Cisco DNA Center cluster for all sites listed in its design hierarchy.
        :return: dict
        """
        self.__all_sites = []
        self.get_site_count()
        (rounds, remainder) = divmod(self.__site_count, SITE_REQUEST_LIMIT)
        if remainder > 0:
            rounds += 1
        if self.__site_count <= NO_SITES:
            raise DnacApiError(MODULE, 'get_all_sites', NO_SITES_ERROR, '', '', '', '', '')
        i = 0
        offset = 1
        filter = '?offset=%i&limit=%i' % (offset, SITE_REQUEST_LIMIT)
        url = '%s%s%s' % (self.dnac.url, self.resource, filter)
        while i < rounds:
            # get the next batch of sites
            response, status = self.crud.get(url,
                                             headers=self.dnac.hdrs,
                                             verify=self.verify,
                                             timeout=self.timeout)
            if status != OK:
                raise DnacApiError(MODULE, 'get_all_sites', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], '')
            self.__all_sites = self.__all_sites + response['response']
            offset += SITE_REQUEST_LIMIT
            i += 1
        return self.__all_sites

    def load_sites(self):
        """
        Instructs the SiteHierarchy object to load all sites from the Cisco DNA Center's site design hierarchy.  This
        method can be used to load a new hierarchy object or to refresh one that has sites which have been added or
        deleted.
        :return: dict
        """
        self.get_all_sites()
        # find the site hierarchy's root: siteNameHierarchy = "Global"
        global_site_node = None
        for site in self.__all_sites:
            if site['siteNameHierarchy'] != GLOBAL_SITE:
                continue
            else:  # found the root
                global_site = Site(self.dnac, GLOBAL_SITE)
                global_site_node = SiteNode(global_site)
                self.add_site_node(global_site_node)
                break
        if global_site_node is None:
            raise DnacApiError(MODULE, 'load_sites', NO_GLOBAL_SITE_ERROR, '', '', str(global_site_node), '', '')
        # starting from the global site, load all children recursively
        #
        #  need a throttle here; this is where the majority of the site calls are being made
        #  perhaps the throttle should be part of a SiteHierarchy instance?
        #
        self.__load_children__(global_site_node)
        return self.__site_nodes

    def add_site_node(self, site_node):
        """
        Adds a SiteNode to the SiteHierarchy's dictionary using the site's hierarch name and its UUID as keys to the
        site's object representation.
        :param site_node: A site hierarchy node representing the site and its children.
        :return: multi_key_dict
        """
        self.__site_nodes[site_node.site.site_name_hierarchy, site_node.site.id] = site_node

    def __load_children__(self, parent_node):
        """
        A hidden method used by the load_sites method to build the site hierarchy.  If a site doesn't exist in the
        Dnac object's api dictionary, this method creates one, installs it and adds a SiteNode to it in the
        SiteHierarchy.  If the site does exist but not in the SiteHierarchy, it installs a SiteNode into the
        SiteHierarchy.

        This method use a recursive call to build the SiteHierarchy.
        :param parent_node: The new site's parent SiteNode.
            type: SiteNode
            required: yes
            default: none
        :return: none
        """
        for site in self.__all_sites:
            if site['siteNameHierarchy'] == GLOBAL_SITE:
                continue
            if site['parentId'] != parent_node.site.id:
                continue
            else:
                if site['siteNameHierarchy'] not in self.dnac.api.keys():
                    # site does not exist; create it now
                    child_site = Site(self.dnac, site['siteNameHierarchy'])
                else:
                    # site exists; get it from Dnac.api
                    child_site = self.dnac.api[site['siteNameHierarchy']]
                    if site['siteNameHierarchy'] in self.__site_nodes.keys():
                        # the site and its site node both exist; nothing to do
                        continue
                # the site's site node does not exist in the hierarchy; create a new site node
                child_node = SiteNode(child_site)
                # add the site node to the parent's children
                parent_node.add_child(child_node)
                # add the site node to the site hierarchy
                self.add_site_node(child_node)
                # find the child node's children (recursive)
                # if the child has no children, there will be no hits on any other site's parentId
                # the method call for the node ends with no action and falls back to the previous call in the stack
                self.__load_children__(child_node)
        return

# end class SiteHierarchy


class SiteNode:
    """
    Class SiteNode is a representation of a site and its children.  Cisco DNA Center's API calls to a site return its
    parent information but not its children.  This class collects all of a site's children as a list for downward
    processing through a site design tree.

    Attributes:
        site: The Site object associated with the SiteNode.
            type: Site object
            default: none
            scope: protected
        children: A list of the site's children sites.
            type: list of Site objects
            default: []
            scope: protected
    """
    def __init__(self, site):
        """
        Creates a new SiteNode based on the site specified.
        :param site: The node's site.
            type: Site object
            required: yes
            default: none
        """
        self.__site = site  # a Site object
        self.__children = []  # list of the site's children sites

    @property
    def site(self):
        """
        Provides a pointer to the node's Site object.
        :return: Site object
        """
        return self.__site

    @property
    def children(self):
        """
        Returns the site's children.
        :return: list of Site objects
        """
        return self.__children

    def add_child(self, child):
        """
        Adds a Site object to the SiteNode as a child of the site's node.
        :param child: A child site of the given node.
            type: Site object
            required: yes
            default: none
        :return: list of Site objects
        """
        return self.__children.append(child)

    def remove_child(self, child):
        """
        Deletes a child Site object from the site's node.
        :param child: One of the site's children.
            type: Site object
            required: yes
            default: none
        :return: list of Site objects
        """
        return self.__children.remove(child)

# end class SiteNode
