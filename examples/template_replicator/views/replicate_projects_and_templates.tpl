<html>
    <h1>Replicate Projects and Templates</h1>
    <p>
    % for result in results:
        {{result}}<br>
    % end
    <p>
    <form action="/select_projects" method="post">
        <input type="hidden" name="source" value="{{source}}">
        <input type="hidden" name="target" value="{{target}}">
        <input type="submit" value="Replicate More Projects from the Same Clusters">
    </form>
    <form action="/select_clusters" method="get">
        <input type="submit" value="Select New Clusters">
    </form>
</html>