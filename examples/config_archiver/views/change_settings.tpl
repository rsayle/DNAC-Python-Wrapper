% current = archive_settings.settings
<html>
    <h1>
        Change Archive Settings
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
    <form action="/submit_new_settings" method="post">
        Timeout <input type="text" name="timeout" value={{current['timeout']}}><br>
        Number of Days <input type="text" name="num_days" value={{current['noOfDays']}}><br>
        Number of Versions <input type="text" name="num_vers" value={{current['noOfVersion']}}><br>
        <input type="submit" value="Submit">
        <input type="submit" value="Cancel" formaction="/manage_settings" method="get">
    </form>
</html>