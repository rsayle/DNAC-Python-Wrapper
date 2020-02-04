from bottle import Bottle, run, template, request
from dnac import Dnac
from dnac.project import Project, STUB_PROJECT
from dnac.template import Template, STUB_TEMPLATE
import copy
import sys
import json

MODULE = 'template_replicator.py'

#clusters_from_config_file = {}
clusters = []
replicator = Bottle()


def get_cluster(cluster_id):
    """
    Retrieved the cluster by a cluster identifier.
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


@replicator.route('/', method='GET')
@replicator.route('/index', method='GET')
@replicator.route('/select_clusters', method='POST')
def select_clusters():
    """
    Passes the list of all clusters loaded during project initialization to the home page.
    :return: Bottle template
    """
    return template('select_clusters', clusters=clusters, method='GET')


@replicator.route('/select_projects', method='POST')
def select_projects():
    """
    From the source and target clusters, prepares a list of each cluster's current projects.
    :return: Bottle template
    """
    source = request.forms.get('source')
    target = request.forms.get('target')
    if source == target:
        raise Exception(
            '%s: select_projects_for_replication: Source and target DNAC clusters cannot be the same' % MODULE
        )
    source_cluster = get_cluster(source)
    target_cluster = get_cluster(target)
    source_projects = {}
    target_projects = {}
    for project in source_cluster.api[STUB_PROJECT].get_all_projects():
        source_projects[project['name']] = project['id']
    for project in target_cluster.api[STUB_PROJECT].get_all_projects():
        target_projects[project['name']] = project['id']
    return template('select_projects', source=source, target=target,
                    source_projects=source_projects, target_projects=target_projects)


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


def copy_project(project, source, target, source_cluster, target_cluster, results):
    """
    Copies the project from the physical source cluster to the physical target cluster.  Loads any Projects missing in
    either the source_cluster or target_cluster DNAC objects.
    :param project: Name of the project to be copied
        type: str
        required: yes
        default: none
    :param source: Name or IP of the source cluster from which the project shall be copied
        type: str
        required: yes
        default: none
    :param target: Name or IP of the target cluster where the project will be copied
        type: str
        required: yes
        default: none
    :param source_cluster: Dnac instance of the source cluster from which the project will be copied
        type: Dnac object
        required: yes
        default: none
    :param target_cluster: Dnac instance of the target cluster where the project will be copied
        type: Dnac object
        required: yes
        default: none
    :param results: The list of results for all attempts to replicate projects and templates
        type: list
        required: yes
        default: none
    :return: the master results list appended with the results of this operation's invocation
    """
    # check the source cluster Dnac for the project
    if project not in source_cluster.api.keys():
        # load the project into the source_cluster
        try:
            Project(source_cluster, project)
        except Exception as error:
            # this should never happen and suggests a problem in select_clusters.tpl or select_clusters()
            raise Exception(
                '%s: replicate_projects_and_templates: Tried to access a project that does not exist in the '
                'source cluster %s: %s' % (MODULE, source, error)
            )
    else:
        # if the Project exists in the source cluster Dnac - refresh its data
        source_cluster.api[project].load_project(project)
    # check the target cluster Dnac for the project
    try:
        if project not in target_cluster.api.keys():
            # if the project does not exist in the target cluster Dnac - add it now
            for p in target_cluster.api[STUB_PROJECT].get_all_projects():
                # search for the project in the physical target cluster, and if found, load it
                if p['name'] == project:
                    Project(target_cluster, project)
                    results.append('Found %s in %s.  Loading its data.' % (project, target))
                    break
            # if it doesn't exist in the physical cluster, create it now
            if project not in target_cluster.api.keys():
                # get a copy of the source Project - using source_cluster will remove its project's templates
                src_proj_copy = copy.deepcopy(source_cluster.api[project].get_project_by_name(project))
                target_cluster.api[STUB_PROJECT].add_project(src_proj_copy.project)
                del src_proj_copy
                results.append('Successfully replicated project %s from %s to %s' % (project, source, target))
        else:
            # if the Project does exist in the target cluster Dnac - refresh its data
            target_cluster.api[project].load_project(project)
            results.append('Found %s in %s.  Refreshing its data.' % (project, target))
    except Exception as error:
        results.append('Failed replicating project %s from %s to %s: %s'
                       'Aborting attempts to add its templates'
                       % (project, source, target, error))
    return results


@replicator.route('/replicate_projects', method='POST')
def replicate_projects():
    """
    Copies the projects selected from the source cluster to the destination cluster.
    :return: Bottle template
    """
    source, target, source_cluster, target_cluster = get_source_and_target(request)
    results = []
    for project in request.forms:
        results = copy_project(project, source, target, source_cluster, target_cluster, results)
    return template('replicate_projects', source=source, target=target, results=results)


def copy_template(template, project, source, target, source_cluster, target_cluster, results):
    """
    Copies a template from the source cluster to the target cluster.  Adds Template objects to both the source Dnac
    and target Dnac cluster instances as necessary.
    :param template: The template to be copied from the source to the target cluster
        type: dict
        required: yes
        default: none
    :param project: The name of the project to which the template belongs
        type: str
        required: yes
        default: none
    :param source: The name or IP of the source cluster
        type: str
        required: yes
        default: none
    :param target: The name or IP of the target cluster
        type: str
        required: yes
        default: none
    :param source_cluster: The Dnac object representation of the source cluster
        type: Dnac object
        required: yes
        default: none
    :param target_cluster: The Dnac object representation of the target cluster
        type: Dnac object
        required: yes
        default: none
    :param results: The master results list of all attempts to replicate projects and templates
        type: list
        required: yes
        default: none
    :return: The master results list appended with the results of this operation's invocation
    """
    if template['name'] not in source_cluster.api.keys():
        # if the Template does not exist in the source cluster Dnac - add it now
        Template(source_cluster, template['name'])
    else:
        # otherwise refresh its data
        source_cluster.api[template['name']].load_template(template['name'])
    # replicate the templates from the source cluster to the target cluster
    ver = 1  # ignore the parent template
    while ver <= len(source_cluster.api[template['name']].versions) - 1:
        # make a copy of each version so as not to clobber the source cluster Project's templates
        version = copy.deepcopy(source_cluster.api[template['name']].versions[ver])
        # add the template
        try:
            if template['name'] not in target_cluster.api.keys():
                # if the template does not yet exist on the target cluster, create it with first version
                target_cluster.api[STUB_TEMPLATE].add_new_template(version, target_cluster.api[project], timeout=10)
            else:
                # if the template does exist, add the next version
                target_cluster.api[template['name']].add_version(version, timeout=10)
            results.append('Successfully replicated version %i of template %s from %s to %s'
                           % (ver, template['name'], source, target))
            # clean up the copy of the source template
            del version
        except Exception as error:
            # add template failed - abort
            results.append('Failed to add version %i of template %s from %s to %s: %s\n'
                           'Aborting the remainder of %s\'s templates'
                           % (ver, template['name'], source, target, error, template['name'])
                           )
            # clean up the copy of the source template
            del version
            break
        # commit the template
        try:
            target_cluster.api[template['name']].commit_template(
                'Committed version %i by %s' % (ver, MODULE), timeout=10
            )
            results.append('Successfully commited version %i of template %s from %s to %s'
                           % (ver, template['name'], source, target))
            # success - increment the version counter and proceed with the next template if available
            ver = ver + 1
        except Exception as error:
            # commit failed - abort
            results.append(
                'Failed to commit version %i of template %s from %s to %s: %s\n'
                'Aborting the remainder of %s\'s versions' %
                (ver, template['name'], source, target, error, template['name'])
            )
            break
    return results

@replicator.route('/replicate_projects_and_templates', method='POST')
def replicate_projects_and_templates():
    """
    Copies the projects selected and all of their templates from the source cluster to the target cluster.
    :return: Bottle template
    """
    source, target, source_cluster, target_cluster = get_source_and_target(request)
    results = []
    for project in request.forms:
        results = copy_project(project, source, target, source_cluster, target_cluster, results)
        for t in source_cluster.api[project].templates:
            results = copy_template(t, project, source, target, source_cluster, target_cluster, results)
    return template('replicate_projects_and_templates', source=source, target=target, results=results)


@replicator.route('/select_templates', method='POST')
def select_templates():
    """
    Prepares the list of templates for each project selected by the end-user.  Only supports projects that exist on
    both the source and target clusters.
    :return: Bottle template
    """
    source, target, source_cluster, target_cluster = get_source_and_target(request)
    if source_cluster == target_cluster:
        raise Exception('Source and target DNAC clusters cannot be the same')

    #
    # templates data structure -  {project_name :  [template_name]}
    #
    source_templates = {}
    target_templates = {}
    existing_target_projects = target_cluster.api[STUB_PROJECT].get_all_projects()
    missing_target_projects = []  # used if a project was selected that does not yet exist on the target cluster

    for project in request.forms:
        # ensure the project exists on the target cluster before listing its templates
        for p in existing_target_projects:
            if p['name'] == project:
                if project not in target_cluster.api.keys():
                    Project(target_cluster, project)
                break
        # if it's not on the target, log the error and move on to the next project
        if project not in target_cluster.api.keys():
            missing_target_projects.append(
                'Project %s does not exist on the target cluster.  Create it first.  Skipping for now.' % project
            )
            request.forms.pop(project)
            break
        # build the source templates list for the project
        if project not in source_cluster.api.keys():
            Project(source_cluster, project)
        else:
            source_cluster.api[project].load_project()
        src_t_list = []
        for t in source_cluster.api[project].templates:
            src_t_list.append(t['name'])
        src_t_list.sort()
        source_templates[project] = copy.deepcopy(src_t_list)
        # build the target templates list for the project
        tgt_t_list = []
        for t in target_cluster.api[project].templates:
            tgt_t_list.append(t['name'])
        tgt_t_list.sort()
        target_templates[project] = copy.deepcopy(tgt_t_list)
    # render the select_templates page
    return template('select_templates', source=source, target=target, projects=request.forms,
                    source_templates=source_templates, target_templates=target_templates,
                    missing_target_projects=missing_target_projects)

@replicator.route('/replicate_templates', method='POST')
def replicate_templates():
    """
    Replicates the templates selected from the select_clusters page.
    :return: Bottle template
    """
    source, target, source_cluster, target_cluster = get_source_and_target(request)
    results = []
    for selection in request.forms:
        # get the project and template names - separator is a % char
        project = selection.split('%')[0]
        tmplt_name = selection.split('%')[1]
        # get the template from the source_cluster Dnac
        for t in source_cluster.api[project].templates:
            if t['name'] == tmplt_name:
                tmplt = copy.deepcopy(t)
                break
        copy_template(tmplt, project, source, target, source_cluster, target_cluster, results)
        del tmplt
    return template('replicate_templates', source=source, target=target, results=results)

# Main Program ########################################################################################################

if __name__ == '__main__':

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
        # create stub projects and templates in the cluster
        Project(dnac, STUB_PROJECT)
        Template(dnac, STUB_TEMPLATE)
        # add the new Dnac instance to the global clusters list
        clusters.append(dnac)

    run(replicator, host='localhost', port=8080, reloader=True, debug=True)

