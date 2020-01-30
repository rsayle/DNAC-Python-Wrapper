% EMPTY = ''
<html>
    <h1 align=center>Replicate Projects</h1>
    <p>
    <form action="/replicate_projects" method="post">
        <table align = center border=1>
            <tr>
                <td>
                    % if source.name != EMPTY:
                        <center><b>Projects available for export on {{source.name}}</b></center>
                        <input type="hidden" name="source" value="{{source.name}}">
                    % elif source.ip != EMPTY:
                        <center><b>Projects available for export on {{source.ip}}</b></center>
                        <input type="hidden" name="source" value="{{source.ip}}">
                    % end
                </td>
                <td>
                    % if target.name != EMPTY:
                        <center><b>Existing projects on {{target.name}}</b></center>
                        <input type="hidden" name="target" value="{{target.name}}"
                    % elif target.ip != EMPTY:
                        <center><b>Existing projects on {{target.ip}}</b></center>
                        <input type="hidden" name="target" value="{{target.ip}}"
                    % end
                </td>
            </tr>
            <tr>
                <td valign="top">
                    % for project in source_projects.keys():
                        <input type="checkbox" name="{{project}}" value="{{project}}">
                            {{project}}
                        </input><br>
                    % end
                </td>
                <td valign="top">
                    % for project in target_projects.keys():
                        {{project}}<br>
                    % end
                </td>
            </tr>
        </table>
        <p>
        <center>
            <input type="submit" value="Replicate Projects Only">
            <input type="submit" value="Replicate Projects with their Templates" method="post"
             formaction="/replicate_projects_with_templates">
        </center>
    </form>
</html>