from dash import Dash, html, dcc, Input, Output, State, register_page, dash_table, callback
import pandas as pd
import dash_bootstrap_components as dbc
import datetime
from datetime import date
import re
import warnings
warnings.filterwarnings(
    action='ignore', category=UserWarning, message=r"Boolean Series.*"
)
from datetime import datetime
import validators
# Register the page with Dash
register_page(__name__, path='/')

# Define dropdowns 
from data import dropdowns as dd

# Sample dataframes for publication history and updates
from data import data_manipulation as dm

# publications_df = dm.load_publications()
# statuses_df = dm.load_statuses()


# Layout
def get_layout():
    layout_lst = []
    
    # Add Publication layout
    Add_New_Publication = html.Div([

        html.H2("Add New Publication"),
        dcc.Input(id='input-name', type='text', placeholder='Publication name', debounce=True, className="input-field"),
        dcc.Input(id='input-link', type='url', placeholder='Publication ticket, link', debounce=True, className="input-field"),
        dcc.Dropdown(id='dropdown-platform', options=[{'label': opt, 'value': opt} for opt in dd.PLATFORM_OPTIONS], placeholder="Testing platform"),
        dcc.Dropdown(id='dropdown-assignee', options=[{'label': opt, 'value': opt} for opt in dd.ASSIGNEE_OPTIONS], placeholder="Assignee"),
        dcc.DatePickerSingle(id='datepicker-start-date', month_format='MMMM YYYY',  display_format='DD-MM-YYYY'),
        html.Label("Select Planned Sites:", style={'display': 'block'}),
        dcc.Dropdown(id='dropdown-sites', multi=True),
        
        html.Label("Select Planned Devices:"),
        dcc.Dropdown(id='dropdown-devices'
                     , multi=True
                     , placeholder="Planned Devices"
                     , options=[{'label': opt, 'value': opt} for opt in dd.DEVICE_OPTIONS]
                     # , value='All'
                    ),
        html.Label("Select Planned Genders:"),
        dcc.Dropdown(id='dropdown-genders'
                     # , multi=True
                     , options=[{'label': opt, 'value': opt} for opt in dd.GENDER_OPTIONS]
                     , placeholder="Planned Genders"
                     , value='All'
                     ),
        
        html.Label("Select Planned Languages:"),
        dcc.Dropdown(id='dropdown-languages'
                     , multi=True
                     , options=[{'label': opt, 'value': opt} for opt in dd.LANGUAGE_OPTIONS]
                     , placeholder="Planned Languages"
                     , value='All'
                    ),
        dcc.Checklist(id='checklist-feature-flag', options=[{'label': 'Feature Flag', 'value': 'true'}], inline=True),

        html.Button("Add Publication",  type="submit", id="btn-add-publication"),
        dbc.Toast(
                "The publication was added successfully!",
                id="pub-created-popup",
                header="Notification",
                is_open=False,
                dismissable=True,  # Allows the user to close it manually
                duration=5000,  # Auto-dismiss after 5000 ms (5 seconds)
                style={
                        "position": "fixed",
                        "bottom": 20,
                        "right": 20,
                        "width": 400,
                        "padding": "10px",
                        "margin": "0",
                        },
                 className="custom-toast"
                ),
        dbc.Toast(
                "The name is already existed",
                id="pub-error-name-popup",
                header="Error!",
                is_open=False,
                dismissable=True,  # Allows the user to close it manually
                duration=5000,  # Auto-dismiss after 5000 ms (5 seconds)
                style={
                        "position": "fixed",
                        "bottom": 20,
                        "right": 20,
                        "width": 400,
                        "padding": "10px",
                        "margin": "0",
                        },
                 className="custom-error-toast"
                )
        

        
    ])
    layout_lst.append(Add_New_Publication)
    
    # Search fileds layout
    Search_publications = html.Div([        
        html.H2("Publication Search"),
        dcc.Dropdown(id='publication-search-platform', multi=True, placeholder='Testing platform'),
        dcc.Dropdown(id='publication-search-assignee', multi=True, placeholder="Assignee"),
        dcc.Dropdown(id='publication-search-status', multi=True, placeholder="Publication status"),
        dcc.DatePickerRange(id='publication-search-date-start', month_format='MMMM YYYY',  display_format='DD-MM-YYYY'),
        html.Button("Clean",  type="submit", id="btn-clean-filters", n_clicks=0 ),

        
    ])
    
    layout_lst.append(Search_publications)
    
    
    # Editable table of publications layout
    
    table = html.Div([  
            html.H2("Publications"),
            dcc.Dropdown(id='table-dropdown-publications', multi=True, placeholder="Select a Publication"),
            dash_table.DataTable(id='table-publications',
                                 columns=[
                                     {"name": "Publication", "id": "Publication", "presentation": "markdown"},
                                     {"name": "Platform", "id": "Platform", "editable": True, "presentation": "dropdown"},
                                     {"name": "Assignee", "id": "Assignee", "editable": True, "presentation": "dropdown"},
                                     {"name": "Start Date", "id": "Start Date", "editable": True, "presentation": "input"},
                                     {"name": "Feature Flag", "id": "Feature Flag", "editable": True, "presentation": "dropdown"},
                                     {"name": "Planned Sites", "id": "Planned Sites", "editable": True, "presentation": "dropdown"},
                                     {"name": "Planned Devices", "id": "Planned Devices", "editable": True, "presentation": "dropdown"},
                                     {"name": "Planned Genders", "id": "Planned Genders", "editable": True, "presentation": "dropdown"},
                                     {"name": "Planned Languages", "id": "Planned Languages", "editable": True, "presentation": "dropdown"},
                                     {"name": "Current Status", "id": "Current Status", "editable": True, "presentation": "dropdown"},
                                     {"name": "Analytics", "id": "Analytics", "editable": True},
                                     {"name": "Publication Name", "id": "Name", "editable": True},
                                     {"name": "Publication Link", "id": "Ticket", "editable": True, "presentation": "input"},
                                 ],
                                 editable=True,
                                 # row_deletable=True,
                                include_headers_on_copy_paste=True,
                                export_format='xlsx',
                                export_headers='display',
                                style_table={'overflowX': 'auto', 'display': 'flex', 'flexWrap': 'wrap', 'maxWidth': '100%'},
                                style_cell={'minWidth': '100px', 'width': '200px', 'maxWidth': '300px'},  # Set column width
                                style_header={'fontWeight': 'bold'},
                                css = [{
                                        "selector": ".Select-menu-outer",
                                        "rule": 'display : block !important'
                                    }]),
            html.Button("Save Updates", id="btn-save-updates", type="submit", n_clicks=0),
            dbc.Toast(
                "Please input data in YYYY-MM-DD format.",
                id="pub-error-date-popup",
                header="The input isn't a date!",
                is_open=False,
                dismissable=True,  # Allows the user to close it manually
                duration=5000,  # Auto-dismiss after 5000 ms (5 seconds)
                style={
                        "position": "fixed",
                        "bottom": 20,
                        "right": 20,
                        "width": 400,
                        "padding": "10px",
                        "margin": "0",
                        },
                 className="custom-error-toast"
                ),
            dbc.Toast(
                "Please input a correct link in the column.",
                id="pub-error-link-popup",
                header="The input isn't a link!",
                is_open=False,
                dismissable=True,  # Allows the user to close it manually
                duration=5000,  # Auto-dismiss after 5000 ms (5 seconds)
                style={
                        "position": "fixed",
                        "bottom": 20,
                        "right": 20,
                        "width": 400,
                        "padding": "10px",
                        "margin": "0",
                        },
                 className="custom-error-toast"
                ),
            dbc.Toast(
                "The changes were saved successfully!",
                id="pub-updates-saved",
                header="Notification",
                is_open=False,
                dismissable=True,  # Allows the user to close it manually
                duration=5000,  # Auto-dismiss after 5000 ms (5 seconds)
                style={
                        "position": "fixed",
                        "bottom": 20,
                        "right": 20,
                        "width": 400,
                        "padding": "10px",
                        "margin": "0",
                        },
                 className="custom-toast"
                )
    ],style={'maxWidth': '100%', 'overflow': 'hidden'})
    
    layout_lst.append(table)
    
    return html.Div(layout_lst)

layout = get_layout

# Callback to choose site options
@callback(
    # Output('dropdown-sites',,
    Output('dropdown-sites', 'options'),
    Output('dropdown-sites', 'placeholder'),
    Output('dropdown-assignee', 'value'),
    Output('dropdown-sites', 'value'),
    Output('dropdown-devices', 'value'),
    Input('dropdown-platform', 'value'),
    
)
def update_sites_dropdown(platform):
    if platform == 'Hard-coded':
        return [{'label': site, 'value': site} for site in dd.SITE_DEV_OPTIONS], 'Planned Sites', "Faza Adiguno", 'All', 'Web'
    
    elif platform == 'Retention':
        return [{'label': site, 'value': site} for site in dd.SITE_RETENTION_OPTIONS]  , 'Planned Sites', '', 'All', "All"
    return [], 'Please choose Testing Platform', '', '', ""

# Callback to show/hide the checklist based on the platform
@callback(
    Output('checklist-feature-flag', 'style'),
    Input('dropdown-platform', 'value')
)

def toggle_checklist(platform):
    if platform == 'Hard-coded':
        return {'display': 'block'}  
    return {'display': 'none'}  



@callback(
    # Output('dropdown-publications', 'options'),
    # Output('table-updates', 'data'),
    Output("pub-created-popup", "is_open"),
    Output("pub-error-name-popup", "is_open"),
    Output("input-name", "className"),
    Output("input-link", "className"),
    Input('btn-add-publication', 'n_clicks'),
    State('input-name', 'value'),
    State('input-link', 'value'),
    State('dropdown-platform', 'value'),
    State('dropdown-assignee', 'value'),
    State('datepicker-start-date', 'date'),
    State('checklist-feature-flag', 'value'),
    State('dropdown-sites', 'value'),
    State('dropdown-devices', 'value'),
    State('dropdown-genders', 'value'),
    State('dropdown-languages', 'value'),

)

def add_new_publication(n_clicks, Name, Ticket, Platform, Assignee, Start_Date, Feature_Flag, Planned_Sites, Planned_Devices, Planned_Genders, Planned_Languages):
    df = dm.load_publications()
    Name_check = Name in df.Name.tolist()
  
    if n_clicks and not Name_check:
        if Name and Ticket:
            dm.add_publication(Name, Ticket, Platform, Assignee, Start_Date, Feature_Flag, Planned_Sites, Planned_Devices, Planned_Genders, Planned_Languages)
            return True, False, "input-field", "input-field"
        check_name = "input-field" if Name else "input-field-error"
        check_link = "input-field" if Ticket else "input-field-error"
        return False, False, check_name, check_link
    elif n_clicks and Name_check:

        return False, True, "input-field-error", "input-field"
    else:
        return False, False, "input-field", "input-field"
    # fix this
        



# callback to filler search parameters
@callback(
    Output('publication-search-assignee', 'options')
    , Output('publication-search-date-start', 'min_date_allowed')
    , Output('publication-search-date-start', 'max_date_allowed')
    , Output('publication-search-platform', 'options')
    , Output('publication-search-platform', 'value')
    , Output('publication-search-assignee', 'value')
    , Output('publication-search-date-start', 'start_date')
    , Output('publication-search-date-start', 'end_date')
    , Output('btn-clean-filters', 'n_clicks')
    , Output('table-dropdown-publications', 'options')
    , Output('table-publications', 'data')
    , Output('publication-search-status', 'options')
    , Output('publication-search-status', 'value')
    , Input('publication-search-platform', 'value')
    , Input('publication-search-assignee', 'value')
    , Input('publication-search-date-start', 'start_date')
    , Input('publication-search-date-start', 'end_date')
    , Input('btn-clean-filters', 'n_clicks')
    , Input('table-dropdown-publications', 'value')
    , Input('publication-search-status', 'value')
   
    # , Input('publication-table', 'table')
    # , prevent_initial_call=True
)

def search(platform, assignees, date_start, date_end, n_clicks, publication, status):
    
    if type(assignees) is str:
        assignees = [assignees]
    # elif assignees == '':
    #     assignees = [""]
        
    if n_clicks > 0:
        platform, assignees ,date_start, date_end, status, n_clicks  = None, None, None, None, None, 0
    
    publications_df = dm.load_publications()
    true = pd.Series([True] * len(publications_df))
    publication_table = publications_df[
                                        (publications_df.Assignee.isin(assignees) if assignees is not None and assignees != [] else true)
                                        &
                                        (pd.to_datetime(publications_df['Start Date']).isin(pd.date_range(date_start,date_end)) if date_start is not None and date_end is not None else true)
                                        & 
                                        (publications_df.Platform.isin(platform) if platform is not None and platform != [] else true)
                                        & 
                                        (publications_df.Name.isin(publication) if publication is not None and publication != "" else true)
        & 
                                        (publications_df['Current Status'].isin(status) if status is not None and status != [] else true)
                                        
        
            
    ]
    
 
    assignees_options = list(set(publication_table.fillna("").Assignee.tolist()))
    publications_options = list(set(publication_table.fillna("").Name.tolist()))
        
    dates = publication_table.loc[publication_table['Start Date'].notna(),'Start Date']
    date_start_default = min(dates) if len(dates) > 0 else None
    date_end_default = max(dates) if len(dates) > 0 else None
    platform_options = list(set(publication_table.Platform.fillna("").tolist()))
    status_options = list(set(publication_table['Current Status'].fillna("").tolist()))
    
    
        
    return assignees_options, date_start_default, date_end_default, platform_options, platform, assignees ,date_start, date_end, n_clicks, publications_options, publication_table.to_dict("records"), status_options, status
    

# Editing the table
@callback(
Output('btn-save-updates', 'n_clicks'),
Output('table-publications', 'data', allow_duplicate=True),
Output('pub-updates-saved', 'is_open'),
Input('table-publications', 'data'),
Input('btn-save-updates', 'n_clicks'),
prevent_initial_call=True

)

def update_table(data, n_clicks):
    if n_clicks > 0:
        df = dm.update_publications(data)
        n_clicks = 0
        return n_clicks, df.to_dict("records"), True
    return n_clicks, data, False

    
    
# Dropdowns of the table
@callback(
Output('table-publications', 'dropdown_conditional'),
Output('table-publications', 'dropdown'),
Output('table-publications', 'data', allow_duplicate=True),
Output('pub-error-date-popup', 'is_open'),
Output('pub-error-link-popup', 'is_open'),
Input('table-publications', 'data'),
Input('table-publications', 'data_previous'),
prevent_initial_call=True

)

def dropdowns(data, data_previous):
    df = pd.DataFrame(data)
    df1 = pd.DataFrame(data_previous)
    if data_previous and df.shape == df1.shape:
        difference = df != df1
        diff_indices = difference.stack()[difference.stack()].index
        if len(diff_indices) == 1:
            differing_cell = diff_indices[0]
            row, col = differing_cell
            value_data = df.at[row, col]
            value_data_previous = df1.at[row, col]
            print(value_data_previous)
            print(value_data)
            if value_data is not None and value_data != "" and col in ("Planned Languages", "Planned Devices", "Planned Sites"):
                if value_data_previous is not None and value_data_previous != "":
                    df.at[row, col] = value_data_previous + ', ' + value_data
                else:
                    df.at[row, col] = value_data
                df.at[row, col] = ', '.join(set(df.at[row, col].split(', ')))
            
            if (value_data is None or value_data == "") and col in ("Feature Flag"):
                df.at[row, col] = False
                
        else:
            print(f"The DataFrames differ in more than one cell or are identical. - {len(diff_indices)}")
            
    data = df.to_dict('records')

    
    language_options = [i for i in list(set(dd.LANGUAGE_OPTIONS+list(df["Planned Languages"].unique()))) if i != '' and i is not None]
    device_options = [i for i in list(set(dd.DEVICE_OPTIONS+list(df["Planned Devices"].unique()))) if i != '' and i is not None]
    site_options = [i for i in list(set(dd.SITE_DEV_OPTIONS+list(df["Planned Sites"].unique()))) if i != '' and i is not None]

    dropdown =     {
                 "Platform": {"options": [{'label': i, 'value':i} for i in dd.PLATFORM_OPTIONS]},
                 "Assignee": {"options": [{'label': i, 'value':i} for i in dd.ASSIGNEE_OPTIONS]},
                 "Planned Genders": {"options": [{'label': i, 'value':i} for i in dd.GENDER_OPTIONS]},
                 "Planned Languages": {"options": [{'label': i, 'value':i} for i in language_options]},
                 "Planned Devices": {"options": [{'label': i, 'value':i} for i in device_options]},
                 "Planned Sites": {"options": [{'label': i, 'value':i} for i in site_options]},
                    
                }
    

    
    dropdown_conditional = [
        {
    
                "if": {
                        'column_id': 'Feature Flag',
                        'filter_query': '{Platform} eq "Hard-coded"'
                },
                
               "options": [{'label': i, 'value':i} for i in ['true', 'false']]
        },
        
        
         {
    
                "if": {
                        'column_id': 'Feature Flag',
                        'filter_query': '{Platform} eq "Retention"'
                },
                
               "options": [{'label': i, 'value':i} for i in ['false']]
        },
        
        
        
         {
    
                "if": {
                        'column_id': 'Current Status',
                        'filter_query': '{Platform} eq "Retention"'
                },
                
               "options": [{'label': i, 'value':i} for i in dd.STATUS_RETENTION_OPTIONS]
        },
        
        
        
         {
    
                "if": {
                        'column_id': 'Current Status',
                        'filter_query': '{Platform} eq "Hard-coded"'
                },
                
               "options": [{'label': i, 'value':i} for i in dd.STATUS_DEVS_FLAG_OPTIONS]
        },
    ]
    
    
    
    date_is_open, link_is_open = False, False

    for row in data:
        date_value = row.get("Start Date", "")
        try:
            if date_value:  # Check if value exists
                datetime.strptime(date_value, "%Y-%m-%d")  # Attempt parsing
        except ValueError:
            row["Start Date"] = ""
            date_is_open = True
            
        link_value = row.get("Ticket", "")
        if not validators.url(link_value):  # Invalid link format
            row["Ticket"] = ""  
            link_is_open = True
            
    
    
    return dropdown_conditional, dropdown, data, date_is_open, link_is_open
                            
        
        