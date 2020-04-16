<html>
    <h1 align="center">Replicate Projects and Templates Results</h1>
    <p>
    % for result in results:
        {{result}}<br>
    % end
    <p>
    <center>
    <form action="/select_projects" method="post">
        <input type="hidden" name="source" value="{{source}}">
        <input type="hidden" name="target" value="{{target}}">
        <input type="submit" value="Replicate More Projects and Templates">
        <input type="submit" value="Select New Clusters" formaction="/select_clusters">
    </form>
    </center>
</html>