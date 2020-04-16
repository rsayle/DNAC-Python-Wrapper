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
        Manage Device Archive Configs
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
            <th></th>
        </tr>
        <form action="/view_config" method="post">
        % for version in device_archive.versions:
            <tr>
                % timestamp.timestamp = version.created_time
                <td>{{timestamp.local_timestamp()}}</td>
                % for key in version.config_files.keys():
                    <td>
                        % file_id = version.config_files[key].id
                        <input type="radio" name="file_id" value="{{file_id}}">{{key}}</input>
                    </td>
                % end
            </tr>
        % end
        <input type="hidden" name="host" value="{{host}}">
        <input type="submit" value="View Config">
        <input type="submit" value="Delete Config" formaction="/delete_config" method="post">
        </form>
        <form action="/manage_archive" method="get">
            <button type="submit">Cancel</button>
        </form>
    </table>
</body>