<html>
<body>
    <h1>Manage Archive</h1>
    <p>
    % if bool(dnac.name):
        Connected to DNA Center cluster: <b>{{dnac.name}}</b>
    % elif bool(dnac.ip):
        Connected to DNA Center cluster: <b>{{dnac.ip}}</b>
    % else:
        Cannot connect to DNA Center cluster.  Please set the FQDN or cluster IP in dnac_config.
    %end
    <p>
    <form action="/manage_archive_configs" method="post">
        <select name="host">
            % for host in hosts:
                <option value="{{host}}">{{host}}</option>
            % end
        </select>
        <input type="submit" value="Manage Archive Configs">
        <input type="submit" value="Add Archive Version" formaction="/add_device_archive_version" method="post">
        <input type="submit" value="Delete Archive Versions" formaction="/delete_device_archive_versions" method="post">
    </form>
    <p>
    <form action="/" method="get">
        <button type="submit" value="cancel">Cancel</button>
    </form>
</body>
</html>