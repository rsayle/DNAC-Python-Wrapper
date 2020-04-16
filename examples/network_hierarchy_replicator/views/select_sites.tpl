<html>
    <h1 align=center>Select Sites</h1>
    <p>
    <form method="post">
        <table align = center border=1>
            <tr>
                <td>
                    <center><b>Sites available for export on {{source}}</b></center>
                    <input type="hidden" name="source" value="{{source}}">
                </td>
                <td>
                    <center><b>Existing sites on {{target}}</b></center>
                    <input type="hidden" name="target" value="{{target}}"
                </td>
            </tr>
            <tr>
                <td valign="top">
                    % for site in source_hierarchy.site_nodes.keys():
                        <input type="checkbox" name="{{site[0]}}" value="{{site[0]}}">
                            {{site[0]}}
                        </input><br>
                    % end
                </td>
                <td valign="top">
                    % for site in target_hierarchy.site_nodes.keys():
                        {{site[0]}}<br>
                    % end
                </td>
            </tr>
        </table>
        <p>
        <center>
            <input type="submit" value="Replicate Sites" formaction="/replicate_sites">
        </center>
    </form>
    <form method="post" action="/select_clusters">
        <center>
            <input type="submit" value="Cancel">
        </center>
    </form>
</html>