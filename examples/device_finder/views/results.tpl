<html>
    <h1 align=center>Results</h1>
    <p>
    <center>
        % if bool(device):
            Found {{target}} in {{cluster}}
            <p>
            <table>
                <tr>
                    <td>
                        <form action={{inventory_url}} target="_blank">
                            <input type="submit" value="Launch Inventory">
                        </form>
                    </td>
                    <td>
                        <form action={{device360_url}} target="_blank">
                            <input type="submit" value="Launch Device 360">
                        </form>
                    </td>
                </tr>
            </table>
        % else:
            Unable to find {{target}}
        % end
        <p>
        <form action="/" method="GET">
            <input type="submit" value="Select a New Device">
        </form>
    </center>
</html>