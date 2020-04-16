<html>
<body>
    <h1>
        Add New Device Archive Version Result
    </h1>
    <p>
    % if bool(dnac.name):
        Connected to DNA Center cluster: <b>{{dnac.name}}</b>
    % elif bool(dnac.ip):
        Connected to DNA Center cluster: <b>{{dnac.ip}}</b>
    % else:
        Cannot connect to DNA Center cluster.  Please set the FQDN or cluster IP in dnac_config.
    %end
    <p>
    Successfully added a new archive version for <em>{{host}}</em>
    <p>
    <form action="/manage_archive_configs" method="post">
        <button name="host" type="submit" value="{{host}}">OK</button>
    </form>
</body>