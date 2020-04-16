<html>
<body>
    Successfully deleted selected archive versions:
    <p>
    % for version in deleted_versions:
        <em>{{version}}</em><br>
    % end
    <p>
    <form action="/manage_archive" method="get">
        <button type="submit" value="ok">OK</button>
     </form>
</body>
</html>