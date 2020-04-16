% NO_TEMPLATES = []
% NO_PROJECTS = {}
<html>
    <h1 align=center>Select Templates</h1>
    <p>
    % for missing in missing_target_projects:
        {{missing}}<br>
    % end
    <p>
    % if projects != NO_PROJECTS:
    <form method="post">
        <table align = center border=1>
        % for project in projects:
            <tr>
                <td colspan="2">
                    <center><b>{{project}}</b></center>
                </td>
            </tr>
            <tr>
                <td>
                    <center><b>Templates available for export on {{source}}</b></center>
                    <input type="hidden" name="source" value="{{source}}">
                </td>
                <td>
                    <center><b>Existing templates on {{target}}</b></center>
                    <input type="hidden" name="target" value="{{target}}"
                </td>
            </tr>
            <tr>
                <td valign="top">
                    % for template in source_templates[project]:
                        % if template != NO_TEMPLATES:
                            <input type="checkbox" name="{{project}}%{{template}}" value="{{project}}%{{template}}">
                                {{template}}
                            </input><br>
                        % end
                    % end
                </td>
                <td valign="top">
                    % for template in target_templates[project]:
                        % if template != NO_TEMPLATES:
                            {{template}}<br>
                        % end
                    % end
                </td>
            </tr>
        % end
        </table>
        <p>
        <center>
            <input type="submit" value="Replicate Templates" formaction="/replicate_templates">
        </center>
    </form>
    % end
    <center>
    <form action="/select_projects" method="post">
        <input type="hidden" name="source" value="{{source}}">
        <input type="hidden" name="target" value="{{target}}">
        <input type="submit" value="Cancel">
    </form>
    </center>
</html>