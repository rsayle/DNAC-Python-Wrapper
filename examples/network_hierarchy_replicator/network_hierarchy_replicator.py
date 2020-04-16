from dnac import Dnac
from dnac.site import Site, STUB_SITE, AREA, BUILDING, FLOOR
from dnac.site_hierarchy import SiteHierarchy, SITE_HIERARCHY_NAME
from bottle import Bottle, run, template, request
import sys
import json

MODULE = 'network_hierarchy_replicator.py'

clusters = []
replicator = Bottle()


def get_cluster(cluster_id):
    """
    Retrieves the cluster by a cluster identifier.
    :param cluster_id: Identifies a cluster by its name or IP address.
        type: str
        required: yes
        default: None
    :return: Dnac object
    """
    for cluster in clusters:
        if cluster_id == cluster.name or cluster_id == cluster.ip:
            return cluster
    else:
        Exception('%s: get_cluster: Could not find cluster %s' % (MODULE, cluster_id))


def get_source_and_target(request):
    """
    Retrieves the source and target cluster names passed from a Bottle template in the request forms.  Also removes
    the source and target from the request's FormsDict so that further processing can be performed on the request's
    list of projects or templates.
    :param request: The request object returned from a Bottle template's posting.
        type: Bottle request object
        required: yes
        default: none
    :return:
        source: The source cluster's name
            type: str
        target: The target cluster's name
            type: str
        source_cluster: The source cluster's Dnac representation
            type: Dnac object
        target_cluster: The target cluster's Dnac representation
            type: Dnac object
    """
    source = request.forms.get('source')
    source_cluster = get_cluster(source)
    request.forms.pop('source')
    target = request.forms.get('target')
    target_cluster = get_cluster(target)
    request.forms.pop('target')
    return source, target, source_cluster, target_cluster


@replicator.route('/', method='GET')
@replicator.route('/index', method='GET')
@replicator.route('/select_clusters', method='POST')
def select_clusters():
    """
    Passes the list of all clusters loaded during project initialization to the home page.
    :return: Bottle template
    """
    return template('select_clusters', clusters=clusters, method='GET')


def get_site_hierarchy(cluster):
    """
    Retrieves the cluster's SiteHierarchy object.
    :param cluster: The Dnac cluster whose SiteHierarchy is required.
        type: Dnac object
        required: yes
        default: none
    :return: SiteHierarchy object
    """
    if bool(cluster.name):
        cluster_id = cluster.name
    elif bool(cluster.ip):
        cluster_id = cluster.ip
    else:
        raise Exception('%s: get_site_hierarchy: Dnac cluster has no name nor IP address' % MODULE)
    site_hierarchy_name = '%s%s' % (cluster_id, SITE_HIERARCHY_NAME)
    if site_hierarchy_name in cluster.api.keys():
        return cluster.api[site_hierarchy_name]
    else:
        return SiteHierarchy(cluster, timeout=60)


@replicator.route('/select_sites', method='POST')
def select_sites():
    """
    Loads the source and target site hierarchies in a web page that allows a user to select the sites from the source
    cluster that should be replicated to the target cluster.
    :return: Bottle template
    """
    source, target, source_cluster, target_cluster = get_source_and_target(request)
    if source == target:
        raise Exception(
            '%s: select_sites: Source and target DNAC clusters cannot be the same' % MODULE
        )
    source_hierarchy = get_site_hierarchy(source_cluster)
    source_hierarchy.load_sites()
    target_hierarchy = get_site_hierarchy(target_cluster)
    target_hierarchy.load_sites()
    return template('select_sites', source=source, target=target,
                    source_hierarchy=source_hierarchy, target_hierarchy=target_hierarchy)


@replicator.route('/replicate_sites', method='POST')
def replicate_sites():
    """
    Iterates through the sites chosen for replication and copies them from the source to the target cluster.
    :return: Bottle template
    """
    source, target, source_cluster, target_cluster = get_source_and_target(request)
    if source == target:
        raise Exception(
            '%s: replicate_sites: Source and target DNAC clusters cannot be the same' % MODULE
        )
    results = []
    for site in request.forms:
        results = copy_site(site, source, target, source_cluster, target_cluster, results)
    return template('replicate_sites', source=source, target=target, results=results)


def copy_site(site, source, target, source_cluster, target_cluster, results):
    """
    Takes the site information from the source cluster and copies it over to the target cluster.
    :param site: The site being copied.
        type: str
        required: yes
        default: none
    :param source: The source cluster's identifier, i.e. it's name or IP address.
        type: str
        required: yes
        default: none
    :param target: The target cluster's identifier, i.e. it's name or IP address.
        type: str
        required: yest
        default: none
    :param source_cluster: The source cluster's Dnac object.
        type: Dnac object
        required: yes
        default: none
    :param target_cluster: The target cluster's Dnac object.
        type: Dnac object
        required: yes
        default: none
    :param results: The list of site replication results.
        type: list
        required: yes
        default: none
    :return: The results list with the addition of the result from calling this function appended to it.
    """
    if site in target_cluster.api.keys():
        results.append('Site %s already exists in target cluster %s. Skipping...' % (site, target))
        return results
    if site not in source_cluster.api.keys():
        results.append('Site %s could not be found in source cluster %s. Skipping...' % (site, source))
        return results
    source_site = source_cluster.api[site]
    # don't add the site if it's parent doesn't exist in the target
    if source_site.parent_name not in target_cluster.api.keys():
        results.append('Parent site %s does not exist for site %s.  Skipping...' % (source_site.parent_name, site))
        return results
    # check the location type and add the site accordingly using the source_site's location values
    try:
        if source_site.location['type'] == AREA:
            target_cluster.api['STUB_SITE'].add_site(
                AREA, source_site.name, source_site.parent_name
            )
        elif source_site.location['type'] == BUILDING:
            target_cluster.api['STUB_SITE'].add_site(
                BUILDING, source_site.name, source_site.parent_name, address=source_site.address,
                latitude=source_site.latitude, longitude=source_site.longitude
            )
        elif source_site.location['type'] == FLOOR:
            target_cluster.api['STUB_SITE'].add_site(
                FLOOR, source_site.name, source_site.parent_name, rf_model=source_site.rf_model,
                width=source_site.width, length=source_site.length, height=source_site.height
            )
        else:
            results.append(
                '%s: copy_site: Unidentifiable site type for site %s: %s. Skipping...' %
                (MODULE, site, source_site.location['type'])
            )
        results.append('Successfully added site %s to target cluster %s' % (site, target))
    except Exception as error:
        results.append('Failed to add site %s to target cluster %s: %s' % (site, target, error))
    return results


# Main Program ########################################################################################################


if __name__ == '__main__':
    """
    usage: site_heirarchy_replicator <clusters_file>
    """

    # read the json encoded config file passed from the CLI
    clusters_file = open(sys.argv[1], mode='r')
    clusters_from_config_file = json.load(clusters_file)
    clusters_file.close()

    # create all the Dnac objects from the clusters that were listed in the config file
    clusters = []
    for cluster in clusters_from_config_file:
        # create a Dnac object
        dnac = Dnac(version=cluster['version'],
                    name=cluster['name'],
                    ip=cluster['ip'],
                    port=cluster['port'],
                    user=cluster['user'],
                    passwd=cluster['passwd'],
                    content_type=cluster['content_type'])
        # create a stub site for adding new sites
        stub_site = Site(dnac, STUB_SITE)
        stub_site.timeout = 60  # my lab's DNAC server is responding slowly; others may not need this
        # add the new Dnac instance to the global clusters list
        clusters.append(dnac)

    run(replicator, host='localhost', port=8088, reloader=True, debug=True)