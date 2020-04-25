% EMPTY=''
<html>
    <head>
        <style>
            table, th, td {
                border: 1px solid black;
            }
        </style>
    </head>
    <h1 align=center>Select Device</h1>
    <p>
    <center>
    % for cluster in clusters:
        % if cluster.name != EMPTY:
            Loaded {{cluster.name}}<br>
        % elif cluster.ip != EMPTY:
            Loaded {{cluster.ip}}<br>
        % else:
            Cluster has no name nor IP.  Check the file used to load your clusters for errors.<br>
        % end
    % end
    </center>
    <p>
    <table align=center>
        <tr>
            <td>
                <form action="/find_device_by_name" method="POST">
                    <label for="find_device_by_name">Hostname</label>
                    <input type="text" id="name" name="name"><br><br>
                    <center>
                        <input type="submit" value="Find Device by Hostname">
                    </center>
                </form>
            </td>
            <td>
                <form action="/find_device_by_ip" method="POST">
                    <label for="find_device_by_ip">IP Address</label>
                    <input type="text" id="ip" name="ip"><br><br>
                    <center>
                        <input type="submit" value="Find Device by IP Address">
                    </center>
                </form>
            </td>
        </tr>
    </table>
</html>