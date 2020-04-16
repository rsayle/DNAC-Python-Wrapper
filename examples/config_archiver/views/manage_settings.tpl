% current = archive_settings.settings
<html>
    <h1>
        Configuration Archive Settings
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
    <table>
        <tr>
            <td>
                Timeout
            </td>
            <td>
                {{current['timeout']}}
            </td>
        </tr>
        <tr>
            <td>
                Number of Days
            </td>
            <td>
                {{current['noOfDays']}}
            </td>
        </tr>
        <tr>
            <td>
                Number of Versions
            </td>
            <td>
                {{current['noOfVersion']}}
            </td>
        </tr>
    </table>
    <table>
        <tr>
            <td>
                <form action="/change_settings" method="get">
                    <button type=submit name=change_settings>
                        Change Settings
                    </button>
                </form>
            </td>
            <td>
                <form action="/" method="get">
                    <button type=submit name=cancel>
                        Cancel
                    </button>
                </form>
            </td>
        <tr>
    </table>
</html>