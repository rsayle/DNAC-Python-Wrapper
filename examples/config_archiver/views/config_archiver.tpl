<html>
    <h1>Cisco DNA Center Configuration Archiver</h1>
    <p>
    % if bool(dnac.name):
        Connected to DNA Center cluster: <b>{{dnac.name}}</b>
    % elif bool(dnac.ip):
        Connected to DNA Center cluster: <b>{{dnac.ip}}</b>
    % else:
        Cannot connect to DNA Center cluster.  Please set the FQDN or cluster IP in dnac_config.
    %end
    <p>
    <table>
        <tr>
            <td>
                <form action="/manage_archive" method="get">
                    <button type="submit">Manage Archive</button>
                </form>
            </td>
            <td>
                <form action="/create_new_archive" method="get">
                    <button type="submit">Create New Archive</button>
                </form>
            </td>
            <td>
                <form action="/manage_settings" method="get">
                    <button type="submit">Manage Archive Settings</button>
                </form>
            </td>
        <tr>
    </table>
</html>