<html>
<body>
    Successfully deleted selected archive versions:
    <p>
    % for version in version_ids:
        <em>{{version}}</em><br>
    % end
    <p>
    <form action="/manage_archive" method="get">
        <button type="submit" value="ok">OK</button>
     </form>
</body>
</html>