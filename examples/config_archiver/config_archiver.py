
from dnac import Dnac
from dnac.config_archive import ConfigArchive
from dnac.config_archive_settings import ConfigArchiveSettings
from dnac.networkdevice import NetworkDevice
from dnac.timestamp import TimeStamp
from dnac.dnacapi import DnacApiError
from bottle import Bottle, run, template, request

MODULE = 'config_archive.py'
SINGLETON = 1

archiver = Bottle()


@archiver.route('/')
@archiver.route('/index')
@archiver.route('/config_archiver')
def config_archiver():
    return template('config_archiver', dnac=dnac, method='GET')


@archiver.route('/manage_settings', method='GET')
def manage_settings():
    return template('manage_settings', dnac=dnac, archive_settings=settings)


@archiver.route('/change_settings', method='GET')
def change_settings():
    return template('change_settings', dnac=dnac, archive_settings=settings)


@archiver.route('/submit_new_settings', method='POST')
def submit_new_settings():
    time = request.forms.get('timeout')
    days = request.forms.get('num_days')
    vers = request.forms.get('num_vers')
    new_settings = {'timeout': time, 'noOfDays': days, 'noOfVersion': vers}
    settings.settings = new_settings
    return template('manage_settings', dnac=dnac, archive_settings=settings)


@archiver.route('/manage_archive', method='GET')
def manage_archive():
    hosts = []
    for device_id in config_archive.archive:
        hostname = device_api.get_device_by_id(device_id)['hostname']
        hosts.append(hostname)
    hosts.sort()
    return template('manage_archive', dnac=dnac, hosts=hosts)


@archiver.route('/manage_archive_configs', method='POST')
def manage_archive_configs():
    host = request.forms.get('host')
    device_api.get_device_by_name(host)
    device_archive = config_archive.archive[device_api.devices['id']]
    return template('manage_archive_configs', dnac=dnac, host=host, device_archive=device_archive, timestamp=timestamp)


@archiver.route('/view_config', method='POST')
def view_config():
    file_name = 'file_%s' % request.forms.get('file_id')
    config = dnac.api[file_name].results
    return template('view_config', config=config)


@archiver.route('/delete_config', method='POST')
def delete_config():
    file_id = request.forms.get('file_id')
    host = request.forms.get('host')
    for device_id, device_archive in config_archive.archive.items():
        for version in device_archive.versions:
            for file_type, file in version.config_files.items():
                if file_id == file.id:
                    target_version = version
    target_version.delete_config_file(file_id)
    return template('delete_config', host=host)


@archiver.route('/add_device_archive_version', method='POST')
def add_device_archive_version():
    host = request.forms.get('host')
    return template('add_device_archive_version', dnac=dnac, host=host)


@archiver.route('/add_new_device_archive_version', method='POST')
def add_new_device_archive_version():
    running = False
    startup = False
    hosts = set()
    requested_config_types = request.forms
    for name, value in requested_config_types.items():
        hosts.add(name.split('_')[0])  # format of name = <hostname>_[running | startup]
        if value == 'running':
            running = True
        elif value == 'startup':
            startup = True
    if len(hosts) != SINGLETON:
        raise Exception('%s: expected one host: received %i: host = %s' % (MODULE, len(hosts), str(hosts)))
    # get the host's id
    host = hosts.pop()
    host_id = device_api.get_device_by_name(host)['id']
    # find the host's device archive
    host_archive = config_archive.archive[host_id]
    host_archive.add_configs_to_archive(running=running, startup=startup)
    return template('add_new_device_archive_version', dnac=dnac, host=host)


@archiver.route('/delete_device_archive_versions', method='POST')
def delete_device_archive_versions():
    host = request.forms.get('host')
    device_api.get_device_by_name(host)
    device_archive = config_archive.archive[device_api.devices['id']]
    return template('delete_device_archive_versions', dnac=dnac, host=host,
                    device_archive=device_archive, timestamp=timestamp)


@archiver.route('/delete_archives', method='POST')
def delete_archives():
    timestamps = request.forms
    hosts = set()
    deleted_versions = []
    # get the hostname
    for name in timestamps:
        hostname = name.split('_')[0]  # format of name = <hostname>_timestamp_<timestamp>
        hosts.add(hostname)
    if len(hosts) != SINGLETON:
        raise Exception('%s: expected one host: received %i: host = %s' % (MODULE, len(hosts), str(hosts)))
    # get the host's id
    host = hosts.pop()
    host_id = device_api.get_device_by_name(host)['id']
    # find the host's device archive
    host_archive = config_archive.archive[host_id]
    # delete the selected versions
    for name, time in timestamps.items():  # format of name = <hostname>_timestamp_<timestamp>
        time = name.split('_')[2]
        for version in host_archive.versions:
            if version.created_time == int(time):
                # found a version to delete
                #
                # DNAC versions 1.3.0.1 and prior:
                # DNAC incorrectly reports a version could not be deleted when in fact it was.  Catch the exception
                # raised by Version and double-check to see if the Version is gone.
                #
                try:
                    host_archive.delete_version(version)
                except DnacApiError as error:
                    error_msg = str(error)
                    failure_reason = error_msg.split(':')[6]
                    if failure_reason.find('Failed to delete archives. Internal Error.'):
                        # double-check that the version was deleted
                        pass
                    else:
                        raise error
                timestamp.timestamp = time
                deleted_versions.append(timestamp.local_timestamp())
    return template('delete_archives', host=host, deleted_versions=deleted_versions)


@archiver.route('/create_new_archive', method='GET')
def create_new_archive():
    # get any devices that don't already have an archive
    candidates = {}
    all_hosts = device_api.get_all_devices()
    for host in all_hosts:
        if host['id'] not in config_archive.archive:
            candidates[host['hostname']] = host['id']
    return template('create_new_archive', dnac=dnac, hosts=candidates)


@archiver.route('/create_new_device_archive', method='POST')
def create_new_device_archive():
    host = request.forms.get('host')
    host_id = device_api.get_device_by_name(host)['id']
    config_archive.add_new_archive(host_id)
    return template('create_new_device_archive', dnac=dnac, host=host)


if __name__ == '__main__':
    dnac = Dnac(name='',
                version='1.3.0.3',
                ip='10.1.41.218',
                port='443',
                user='admin',
                passwd='P@$$w0rd',
                content_type='application/json')
    timestamp = TimeStamp()
    device_api = NetworkDevice(dnac, 'deviceapi')
    if bool(dnac.name):
        settings = ConfigArchiveSettings(dnac, dnac.name)
        config_archive = ConfigArchive(dnac, dnac.name)
        config_archive.load_all_archives()
    elif bool(dnac.ip):
        settings = ConfigArchiveSettings(dnac, dnac.name)
        config_archive = ConfigArchive(dnac, dnac.name)
        config_archive.load_all_archives()
    else:
        print('Could not connect to DNA Center.  Set the FQDN or IP in dnac_config.')
        exit(1)
    run(archiver, host='localhost', port=8080, reloader=True, debug=True)