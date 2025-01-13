import dash 
import dash_bootstrap_components as dbc
from dash import html



# Initialize the Dash app
app = dash.Dash(
    __name__
    , use_pages=True
    , external_stylesheets=[dbc.themes.MINTY, dbc.icons.FONT_AWESOME]
)
app.title = "Publication Managment System"
app.layout = dbc.Container(dash.page_container, fluid=True)


# Main layout with navigation bar and page content placeholder
app.layout = html.Div(
    [
        # Navbar spanning the full width
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Development View", href="/dev_view")),
                dbc.NavItem(dbc.NavLink("Clash Check", href="/clash_check")),
            ],
            brand="Publication Management System",
            color="primary",
            dark=True,
            fluid=True,  # Make navbar fluid to span the full width
        ),
        
        # Page content area
        html.Div(id="page-content"),
        dash.page_container,  # Placeholder for dynamic content
    ],
    style={'margin': '0', 'padding': '0'},  # Remove margin and padding from body
    className="m-0",  # Removes any extra margin on the container
)

server = app.server
if __name__ == "__main__":
    app.run_server(debug=True)
