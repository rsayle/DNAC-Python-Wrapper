<html>
<head>
    <style>
        table, th, td {
            border: 1px solid black;
            empty_cells: show;
            text-align: left;
            vertical-align: middle;
        }
    </style>
</head>
<body>
    <h1>
        Delete Device Archive Versions
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
    Configuration archive for <em>{{host}}</em>
    <table>
        <tr>
            <th>Version</th>
            <th></th>
        </tr>
        <form action="/delete_archives" method="post">
        % for version in device_archive.versions:
            <tr>
                % timestamp.timestamp = version.created_time
                <td>{{timestamp.local_timestamp()}}</td>
                    <td>
                        <input type="checkbox" name="{{host}}_timestamp_{{timestamp.timestamp}}"
                         value="{{timestamp.timestamp}}">
                    </td>
        % end
            </tr>
        % end
        <input type="submit" value="Submit">
        </form>
        <form action="/manage_archive" method="get">
            <button type="submit" value="cancel">Cancel</button>
        </form>
    </table>
</body>