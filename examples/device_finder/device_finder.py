from dnac import Dnac
from dnac.site import Site, STUB_SITE
from dnac.networkdevice import NetworkDevice, STUB_DEVICE
from dnac.dnacapi import DnacApiError
from bottle import Bottle, run, template, request
import sys
import json

MODULE = 'device_finder.py'

NO_CLUSTER_NAME_NOR_IP = "Cluster has no name nor IP address"
HTTPS = 'https://'
INVENTORY_URI = '/dna/provision/devices/inventory?devices-view=inventoryView&selectedSite='
DEVICE360_URI = '/dna/assurance/home#networkDevice/'

clusters = []
finder = Bottle()


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


def get_cluster_id(cluster):
    if cluster.name != "":
        return cluster.name
    elif cluster.ip != "":
        return cluster.ip
    else:
        raise Exception("%s: %s" % (MODULE, NO_CLUSTER_NAME_NOR_IP))


@finder.route('/', method='GET')
@finder.route('/index', method='GET')
@finder.route('/select_device', method='POST')
def select_device():
    return template('select_device', clusters=clusters, method='GET')


def get_site(device, cluster):
    details = device.get_device_detail_by_name(device.devices['id'])
    location = details['location']
    if location in cluster.api.keys():
        location_id = cluster.api[location].id
    else:
        site = Site(cluster, location)
        location_id = site.id
    return location_id


@finder.route('/find_device_by_name', method='POST')
def find_device_by_name():
    name = request.forms.get('name')
    device = None
    target_cluster = None
    cluster_id = None
    inventory_url = ''
    device360_url = ''
    for cluster in clusters:
        # if the device has been cached, return it
        if name in cluster.api.keys():
            device = cluster.api[name]
            target_cluster = cluster
            cluster_id = get_cluster_id(cluster)
            break
        # otherwise, try finding it in the current cluster
        else:
            try:
                # an exception will be thrown if it's not in the cluster
                result = cluster.api[STUB_DEVICE].get_device_by_name(name)
                # otherwise, it does exist in the physical cluster; cache it in the cluster and return it
                device = NetworkDevice(cluster, result['hostname'])
                target_cluster = cluster
                cluster_id = get_cluster_id(cluster)
                break
            except DnacApiError:
                # device not found; try the next cluster
                continue
    # if the device was found, get the associated site info in case the user wants to cross-launch into inventory
    if bool(device):
        details = device.get_device_detail_by_name(name)
        location = details['location']
        if location in target_cluster.api.keys():
            site = target_cluster.api[location]
        else:
            site = Site(target_cluster, location)
        inventory_url = '%s%s%s%s' % (HTTPS, cluster_id, INVENTORY_URI, site.id)
        device360_url = '%s%s%s%s' % (HTTPS, cluster_id, DEVICE360_URI, device.get_id_by_device_name(name))
    return template('results', target=name, cluster=cluster_id, device=device, inventory_url=inventory_url,
                    device360_url=device360_url, method='GET')


@finder.route('/find_device_by_ip', method='POST')
def find_device_by_ip():
    ip = request.forms.get('ip')
    device = None
    target_cluster = None
    cluster_id = None
    inventory_url = ''
    device360_url = ''
    for cluster in clusters:
        # if the device has been cached, return it
        if ip in cluster.api.keys():
            device = cluster.api[ip]
            target_cluster = cluster
            cluster_id = get_cluster_id(cluster)
            break
        # otherwise, try finding it in the current cluster
        else:
            try:
                # an exception will be thrown if it's not in the cluster
                result = cluster.api[STUB_DEVICE].get_device_by_ip(ip)
                # otherwise, it does exist in the physical cluster; cache it in the cluster and return it
                device = NetworkDevice(cluster, result['managementIpAddress'])
                target_cluster = cluster
                cluster_id = get_cluster_id(cluster)
                break
            except DnacApiError:
                # device not found; try the next cluster
                continue
    # if the device was found, get the associated site info in case the user wants to cross-launch into inventory
    if bool(device):
        device_by_ip = device.get_device_by_ip(ip)
        details = device.get_device_detail_by_name(device_by_ip['hostname'])
        location = details['location']
        if location in target_cluster.api.keys():
            site = target_cluster.api[location]
        else:
            site = Site(target_cluster, location)
        inventory_url = '%s%s%s%s' % (HTTPS, cluster_id, INVENTORY_URI, site.id)
        device360_url = '%s%s%s%s' % (HTTPS, cluster_id, DEVICE360_URI, device.devices['id'])
    return template('results', target=ip, cluster=cluster_id, device=device, inventory_url=inventory_url,
                    device360_url=device360_url, method='GET')


##### Main Program #####################################################################################################

if __name__ == '__main__':
    """
    usage: device_finder <clusters_file>: finds a network device among multiple DNA Center clusters.
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
        # create a stub network device for finding devices
        stub_device = NetworkDevice(dnac, STUB_DEVICE)
        # add the new Dnac instance to the global clusters list
        clusters.append(dnac)

    run(finder, host='localhost', port=8088, reloader=True, debug=True)
