<html>
    <h1>
        Create New Archive
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
    % if not bool(hosts):
        All devices already have archives.
        <p>
        <form action="/" method="get">
            <button type="submit" value="ok">OK</button>
        </form>
    % else:
        <form action="/create_new_device_archive" method="post">
        <select name="host">
            % for host in hosts:
                <option value="{{host}}">{{host}}</option>
            % end
        </select>
        <input type="submit" value="Add Archive">
    </form>
    <form action="/" method="get">
        <input type="submit" value="Cancel">
    </form>
    </form>
    % end
</html>