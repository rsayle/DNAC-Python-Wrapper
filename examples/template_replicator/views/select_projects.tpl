<html>
    <h1 align=center>Select Projects</h1>
    <p>
    <form method="post">
        <table align = center border=1>
            <tr>
                <td>
                    <center><b>Projects available for export on {{source}}</b></center>
                    <input type="hidden" name="source" value="{{source}}">
                </td>
                <td>
                    <center><b>Existing projects on {{target}}</b></center>
                    <input type="hidden" name="target" value="{{target}}"
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
            <input type="submit" value="Replicate Projects" formaction="/replicate_projects">
            <input type="submit" value="Replicate Projects and Templates" formaction="/replicate_projects_and_templates">
            <input type="submit" value="Select Templates" formaction="/select_templates">
        </center>
    </form>
    <form method="post" action="/select_clusters">
        <center>
            <input type="submit" value="Cancel">
        </center>
    </form>
</html>