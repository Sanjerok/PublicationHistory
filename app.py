import dash 
import dash_bootstrap_components as dbc
from dash import html

# Initialize the Dash app
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.MINTY, dbc.icons.FONT_AWESOME],
    prevent_initial_callbacks='initial_duplicate'
)
app.title = "Publication Management System"

# Define the layout once with both navbar and page container
app.layout = html.Div(
    [
        # Navbar spanning the full width
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Add Publication", href="/")),
                dbc.NavItem(dbc.NavLink("Add Status", href="/add_status")),
                dbc.NavItem(dbc.NavLink("Development View", href="/dev_view")),*
                dbc.NavItem(dbc.NavLink("Retention view", href="/ret_view")),
            ],
            brand="Publication Management System",
            color="primary",
            dark=True,
            fluid=True,
        ),
        
        # Container for page content
        dbc.Container(
            dash.page_container,
            fluid=True,
            className="pt-4"  # Add some padding at the top
        ),
    ],
    style={'margin': '0', 'padding': '0'},
    className="m-0",
)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

