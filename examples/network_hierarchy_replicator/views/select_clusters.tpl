% EMPTY=''
<html>
    <h1 align=center>Select Clusters</h1>
    <p>
    <table align=center>
        <tr>
            <td>
                <b>Source Cluster</b><br>
                <select name="source" form="select_sites">
                % for cluster in clusters:
                    % if cluster.name != EMPTY:
                        <option value="{{cluster.name}}">{{cluster.name}}</option>
                    % elif cluster.ip != EMPTY:
                        <option value="{{cluster.ip}}">{{cluster.ip}}</option>
                    % end
                % end
                </select>
            </td>
            <td>
                <b>Target Cluster</b><br>
                <select name="target" form="select_sites">
                % for cluster in clusters:
                    % if cluster.name != EMPTY:
                        <option value="{{cluster.name}}">{{cluster.name}}</option>
                    % elif cluster.ip != EMPTY:
                        <option value="{{cluster.ip}}">{{cluster.ip}}</option>
                    % end
                % end
                </select>
            </td>
        </tr>
    </table>
    <p>
    <center>
        <form id="select_sites" method="post">
            <input type="submit" value="Continue" formaction="/select_sites">
        </form>
    </center>
</html>