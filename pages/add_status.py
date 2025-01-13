import dash
from dash import html, dcc, callback, Input, Output, State, no_update, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import data.data_manipulation as dm
import data.dropdowns as dd
from dash.dependencies import ClientsideFunction
import time
from dash import dash_table
from dash.exceptions import PreventUpdate
from dash.dash_table.Format import Group

# Update the register_page call to include the path
dash.register_page(
    __name__,
    path='/add_status',  # This should match the href in your navbar
    name='Add Status'    # This is the display name
)

def get_layout():


    

    return html.Div([

        # Success notification popup
        dbc.Toast(
            "Changes saved successfully!",
            id="status-success-popup",
            header="Notification",
            is_open=False,
            dismissable=True,
            duration=5000,
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
        
        # Error notification popup
        dbc.Toast(
            children="",  # This will be updated by the callback
            id="status-error-popup",  # Changed from status-error-popup-text
            header="Error!",
            is_open=False,
            dismissable=True,
            duration=5000,
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
        
        html.H2("Add Status"),
        
        # Publication Dropdown with initial options
        html.Label("Select Publication: *", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='status-publication-dropdown',
            placeholder="Select a publication",
            
        ),
        
        # Publication Info Card
        html.Div(
            dbc.Card([
                dbc.CardBody(id='publication-info-content')
            ]),
            id='publication-info-wrapper',
            style={'display': 'none'}
        ),
        
        # Date Picker (add this before Status Dropdown)
        html.Label("Select Date: *", style={'font-weight': 'bold'}),
        dcc.DatePickerSingle(
            id='status-date',
            date=datetime.now().date(),
            display_format='YYYY-MM-DD'
        ),
        
        # Status Dropdown
        html.Label("Select Status: *", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='status-action-dropdown',
            options=[],
            placeholder="Select status"
        ),
        
        # Sites Dropdown
        html.Label("Select Sites: *", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='status-sites-dropdown',
            options=[],
            multi=True,
            placeholder="Select sites"
        ),
        
        # Devices Dropdown
        html.Label("Select Devices: *", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='status-devices-dropdown',
            options=[],
            multi=True,
            placeholder="Select devices"
        ),
        
        # Genders Dropdown
        html.Label("Select Genders: *", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='status-genders-dropdown',
            options=[],
            placeholder="Select genders"
        ),
        
        # Languages Dropdown
        html.Label("Select Languages: *", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='status-languages-dropdown',
            options=[],
            multi=True,
            placeholder="Select languages"
        ),
        
        # Comment Input (optional)
        html.Label("Comment:"),
        dcc.Input(
            id='status-comment-input',
            type='text',
            placeholder="Add a comment (optional)",
            style={'width': '100%', 'margin-bottom': '10px'}
        ),
        

        
        # Submit Button
        html.Button(
            'Add Status',
            id='submit-status-button',
            n_clicks=0,
            style={'margin-top': '20px'}
        ),
        
        # Add horizontal line to separate sections
        html.Hr(style={'margin': '30px 0'}),
        
        # Status Table Section
        html.H2("Status History"),
        
        # Filters row
        dbc.Row([
            dbc.Col([
                html.Label("Filter by Platform:"),
                dcc.Dropdown(
                    id='table-platform-filter',
                    placeholder="Select platform",
                    clearable=True
                )
            ], width=3),
            
            dbc.Col([
                html.Label("Filter by Assignee:"),
                dcc.Dropdown(
                    id='table-assignee-filter',
                    placeholder="Select assignee",
                    clearable=True
                )
            ], width=3),
            
            dbc.Col([
                html.Label("Filter by Status:"),
                dcc.Dropdown(
                    id='table-status-filter',
                    placeholder="Select status",
                    clearable=True
                )
            ], width=3),
            
            dbc.Col([
                html.Label("Filter by Publication:"),
                dcc.Dropdown(
                    id='table-publication-filter',
                    placeholder="Select publication",
                    clearable=True
                )
            ], width=3)
        ], className='mb-3'),
        
        # Publication Info Card for table filter
        html.Div(
            dbc.Card([
                dbc.CardBody(id='table-publication-info-content')
            ]),
            id='table-publication-info-wrapper',
            style={'display': 'none', 'margin-bottom': '20px'}
        ),
        
        # Status Table
        html.Div([
            dash_table.DataTable(
                id='status-table',
                columns=[
                    {'name': 'Status', 'id': 'Action', 'type': 'text', 'presentation': 'dropdown'},
                    {'name': 'Date', 'id': 'Date', 'type': 'text'},
                    {'name': 'Sites', 'id': 'Sites', 'type': 'text', 'presentation': 'dropdown'},
                    {'name': 'Devices', 'id': 'Devices', 'type': 'text', 'presentation': 'dropdown'},
                    {'name': 'Genders', 'id': 'Genders', 'type': 'text', 'presentation': 'dropdown'},
                    {'name': 'Languages', 'id': 'Languages', 'type': 'text', 'presentation': 'dropdown'},
                    {'name': 'Comment', 'id': 'Comment', 'type': 'text'},
                    # {'name': 'StatusID', 'id': 'StatusID', 'type': 'text'},
                ],
                data=[],
                editable=True,
                style_table={
                    'overflowX': 'auto',
                    'minWidth': '100%'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '150px',  # Ensure cells are wide enough
                    'maxWidth': '300px',   # Limit maximum width
                    
                },
                style_cell_conditional=[
                    {
                        'if': {'column_id': col},
                        'cursor': 'pointer',
                        'backgroundColor': '#fafafa'
                    } for col in ['Action', 'Sites', 'Devices', 'Genders', 'Languages']
                ],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'padding': '10px'
                },
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_data_conditional=[
                    {
                        'if': {'column_id': col},
                        'backgroundColor': '#fafafa',
                        'cursor': 'pointer'
                    } for col in ['Action', 'Sites', 'Devices', 'Genders', 'Languages']
                ],
                page_size=10,
                sort_action='native',
                row_deletable=True,
                css=[
                    # {
                    #     'selector': '.Select-clear',  # Target the clear ("x") button
                    #     'rule': 'display: none !important;'
                    # },
                    # {
                    #     'selector': '.Select-clear-zone',  # Target the clear button zone
                    #     'rule': 'display: none !important;'
                    # },
                     {
                        'selector': '.Select-menu-outer',
                        'rule': 'display: block !important'
                    },
                    {
                        'selector': '.Select-arrow',
                        'rule': 'display: block !important'
                    },
                    {
                        'selector': '.Select',
                        'rule': 'z-index: 100 !important'
                    }
                    
                ]
            ),
        ], className='mb-3', style={'padding': '20px'}),
        
        # Save Updates Button
        html.Button(
            "Save Updates",
            id="btn-save-updates-status",
            className="mb-3",
            style={'margin-top': '10px'}
        ),
        
        
        # Date validation error toast
        dbc.Toast(
            id='status-date-error-popup',
            header="Error",
            is_open=False,
            duration=5000,
            icon="danger",
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
        
        # Save error toast
        dbc.Toast(
            id='status-save-error-popup',
            header="Error",
            is_open=False,
            icon="danger",
            dismissable=True,
            duration=5000,
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
        
        # Publication Details Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Publication Details")),
            dbc.ModalBody(id="publication-details-content"),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-pub-details", className="ms-auto", n_clicks=0)
            ),
        ], id="publication-details-modal", size="lg", is_open=False),
        
     
    ])


@callback(
    [Output('status-success-popup', 'is_open', allow_duplicate=True),
     Output('status-error-popup', 'is_open', allow_duplicate=True),
     Output('status-error-popup', 'children', allow_duplicate=True)],
    [Input('submit-status-button', 'n_clicks')],
    [State('status-publication-dropdown', 'value'),
     State('status-action-dropdown', 'value'),
     State('status-date', 'date'),
     State('status-sites-dropdown', 'value'),
     State('status-devices-dropdown', 'value'),
     State('status-genders-dropdown', 'value'),
     State('status-languages-dropdown', 'value'),
     State('status-comment-input', 'value')],
    prevent_initial_call=True
)
def add_status_callback(n_clicks, pub_id, status, date, sites, devices, genders, languages, comment):
    if not n_clicks:
        return no_update, no_update, no_update
    
    # Check each required field and collect missing ones
    missing_fields = []
    if not pub_id:
        missing_fields.append("Publication")
    if not status:
        missing_fields.append("Status")
    if not date:
        missing_fields.append("Date")
    if not sites:
        missing_fields.append("Sites")
    if not devices:
        missing_fields.append("Devices")
    if not genders:
        missing_fields.append("Genders")
    if not languages:
        missing_fields.append("Languages")
    
    if missing_fields:
        error_message = f"Please fill in all required fields: {', '.join(missing_fields)}"
        return False, True, error_message
    
    try:
        dm.add_status(pub_id, status, date, sites, devices, genders, languages, comment)
        return True, False, "The status has been added successfully"  # Success popup
    except Exception as e:
        error_message = f"Error adding status: {str(e)}"
        return False, True, error_message  # Error popup with message

# Restore the publication details callback
@callback(
    Output('publication-info-content', 'children'),
    Output('publication-info-wrapper', 'style'),
    Input('status-publication-dropdown', 'value')
)
def update_publication_info(selected_pub_id):
    if selected_pub_id is None:
        return None, {'display': 'none'}
    
    publications_df = dm.load_publications()
    
    # Convert selected_pub_id and DataFrame PubID to strings for comparison
    selected_pub_id = str(selected_pub_id)
    publications_df['PubID'] = publications_df['PubID'].astype(str)
    
    matching_pubs = publications_df[publications_df['PubID'] == selected_pub_id]
    
    if matching_pubs.empty:
        return None, {'display': 'none'}
        
    pub_info = matching_pubs.iloc[0]
    
    parameters = ['Name', 'Platform', 'Assignee', 'Start Date', 'Current Status']
    
    if pub_info['Platform'] == 'Hard-coded':
        parameters.append('Feature Flag')
    
    card_content = dm.card_content_insert(parameters, pub_info)
    
    return card_content, {'display': 'block', 'margin-bottom': '20px'}

# Update status options based on selected publication
@callback(
   
    Output('status-action-dropdown', 'options'),
    Output('status-publication-dropdown', 'options'),
    Input('status-publication-dropdown', 'value'),

)
def update_status_options(selected_pub_id,):

    if selected_pub_id is None or selected_pub_id == '':
        return [], dm.get_publication_options(dm.load_publications())
    
    # Load publications data
    publications_df = dm.load_publications()
    
    # Convert selected_pub_id to integer for comparison
    selected_pub_id = int(selected_pub_id)
    
    # Get selected publication info
    matching_pubs = publications_df[publications_df['PubID'] == selected_pub_id]
    if matching_pubs.empty:
        return [], dm.get_publication_options(publications_df)
        
    pub_info = matching_pubs.iloc[0]
    
    # Determine which status options to use
    if pub_info['Platform'] == 'Hard-coded':
        if pub_info['Feature Flag']:
            options = dd.STATUS_DEVS_FLAG_OPTIONS
        else:
            options = dd.STATUS_DEVS_NO_FLAG_OPTIONS
    else:  # Retention platform
        options = dd.STATUS_RETENTION_OPTIONS
    
    return [{'label': status, 'value': status} for status in options], dm.get_publication_options(publications_df)



# Devices dropdown callback
@callback(
    [Output('status-devices-dropdown', 'options'),
     Output('status-devices-dropdown', 'value')],
    [Output('status-sites-dropdown', 'options'),
     Output('status-sites-dropdown', 'value')],
    [Output('status-languages-dropdown', 'options'),
     Output('status-languages-dropdown', 'value')],
    [Output('status-genders-dropdown', 'options'),
     Output('status-genders-dropdown', 'value')],
    Input('status-publication-dropdown', 'value')
)
def update_all_dropdowns(selected_pub_id):
    empty_result = [], None, [], None, [], None, [], None
    
    if selected_pub_id is None:
        return empty_result
    
    publications_df = dm.load_publications()
    matching_pubs = publications_df[publications_df['PubID'].astype(str) == str(selected_pub_id)]
    
    if matching_pubs.empty:
        return empty_result
        
    pub_info = matching_pubs.iloc[0]
    
    def get_options_and_default(field_name, expansion_func, extra_args=None):
        planned_values = pub_info[f'Planned {field_name}']
        if not planned_values:
            return [], None
            
        expanded = expansion_func(planned_values, *extra_args) if extra_args else expansion_func(planned_values)
        options = [{'label': x, 'value': x} for x in expanded]
        
        # Set default value
        planned_list = planned_values.split(', ') if planned_values else []
        default_value = None
        if len(planned_list) == 1:
            default_value = planned_list[0]
        elif 'All' in planned_list:
            default_value = 'All'
            
        return options, default_value
    
    # Get options for each dropdown
    devices_options, devices_default = get_options_and_default('Devices', dm.expand_devices_options)
    sites_options, sites_default = get_options_and_default('Sites', dm.expand_sites_options, [pub_info['Platform']])
    languages_options, languages_default = get_options_and_default('Languages', dm.expand_languages_options)
    genders_options, genders_default = get_options_and_default('Genders', dm.expand_genders_options)
    return (
        devices_options, devices_default,
        sites_options, sites_default,
        languages_options, languages_default,
        genders_options, genders_default
    )

# Status table filters
@callback(
    [Output('table-assignee-filter', 'options'),
     Output('table-status-filter', 'options'),
     Output('table-publication-filter', 'options'),
     Output('table-platform-filter', 'options'),
     Output('table-assignee-filter', 'value'),
     Output('table-status-filter', 'value'),
     Output('table-publication-filter', 'value'),
     Output('table-platform-filter', 'value')],
    [Input('table-platform-filter', 'value'),
     Input('table-assignee-filter', 'value'),
     Input('table-status-filter', 'value'),
     Input('table-publication-filter', 'value')]
    )
def update_table_filters(platform, assignee, status, selected_pub_id):
    assignee_options, status_options, pub_options, platform_options, dropdown = [], [], [], [], {}

    
   

    filtered_pubs = dm.get_publication_statuses(platform=platform,
                                                        assignee=assignee,
                                                        status=status)

    if platform is not None and platform != '':
        filtered_pubs = filtered_pubs[filtered_pubs['Platform'].fillna('') == platform]
    if assignee is not None and assignee != '':
        filtered_pubs = filtered_pubs[filtered_pubs['Assignee'].fillna('') == assignee]
    if status is not None and status != '':
        filtered_pubs = filtered_pubs[filtered_pubs['Current Status'].fillna('') == status]

    if platform != '' and platform is not None and platform not in filtered_pubs['Platform'].unique():
        platform = None
    if assignee != '' and assignee is not None and assignee not in filtered_pubs['Assignee'].unique():
        assignee = None
    if  status != '' and status is not None and status not in filtered_pubs['Current Status'].unique():
        status = None
    if  selected_pub_id != '' and selected_pub_id is not None and int(selected_pub_id) not in filtered_pubs['PubID'].unique():
        selected_pub_id = None
    if len(filtered_pubs.PubID.unique()) == 1:
        selected_pub_id = filtered_pubs['PubID'].unique()[0]

    # Generate options from filtered publications data
    assignee_options = [
        {'label': x, 'value': x} 
        for x in sorted(filtered_pubs['Assignee'].fillna('').unique())
    ] or [{'label': 'No options available', 'value': ''}]

    status_options = [
        {'label': x, 'value': x} 
        for x in sorted(filtered_pubs['Current Status'].fillna('').unique())
    ] or [{'label': 'No options available', 'value': ''}]

    pub_options = [
        {'label': f"{row['Name']} (ID: {row['PubID']})", 'value': str(row['PubID'])}
        for _, row in filtered_pubs[['Name', 'PubID']].drop_duplicates().iterrows()
    ] or [{'label': 'No options available', 'value': ''}]

    platform_options = [
        {'label': x, 'value': x} 
        for x in sorted(filtered_pubs['Platform'].unique())
    ] or [{'label': 'No options available', 'value': ''}]
        
    return assignee_options, status_options, pub_options, platform_options, assignee, status, selected_pub_id, platform

@callback(
    [Output('status-table', 'data'),
     Output('status-table', 'dropdown'),
     Output('status-date-error-popup', 'is_open'),
     Output('status-date-error-popup', 'children'),
     Output('status-success-popup', 'is_open'),
     Output('status-save-error-popup', 'is_open'),
     Output('status-save-error-popup', 'children')],
    [Input('table-publication-filter', 'value'),
     Input('status-table', 'data'),
     Input('status-table', 'data_previous'),
     Input('btn-save-updates-status', 'n_clicks'),
     
     ]
    )
def update_status_table(selected_pub_id, data, data_previous, n_clicks):
    
    dropdown ={}
    table_data = data

    date_error_open, success_open, save_error_open = False, False, False
    date_error_msg, save_error_msg = "", ""
    update_dropdown = (False, None, None)
    triggered = ctx.triggered_id
    print(f'triggered: {triggered}')
    if triggered == 'table-publication-filter' and selected_pub_id:
        table_data = dm.get_publication_statuses(
            pub_id=selected_pub_id,
        ).to_dict('records')

    elif triggered == "status-table":    
    # Handle row deletion or cell updates
        if data_previous: 
            df = pd.DataFrame(table_data) if data else pd.DataFrame()
            df_prev = pd.DataFrame(data_previous)
            if df.PubID.unique()[0] == df_prev.PubID.unique()[0]:
            # Check if rows were deleted by comparing indices
                if len(df) < len(df_prev):
                    # Keep the sorted data after deletion
                    if 'Date' in df.columns:
                        df = df.sort_values(['Date', 'StatusID'])
                    table_data = df.to_dict('records')
                    
                # Handle cell updates for concatenation
                elif df.shape == df_prev.shape:
                    difference = df != df_prev
                    diff_indices = difference.stack()[difference.stack()].index
                    if len(diff_indices) == 1:
                        row, col = diff_indices[0]
                        value_data = df.at[row, col]
                        value_data_previous = df_prev.at[row, col]

                    
                        if value_data is not None and value_data != "" and col in ("Sites", "Devices", "Languages"):
                            if value_data_previous is not None and value_data_previous != "":
                                values = set(value_data_previous.split(', '))
                                value_data = value_data.split(', ')
                                values.update(value_data)
                                value_data = ', '.join(sorted(set(values)))
                                update_dropdown = (True, col, value_data)
                           
                            df.at[row, col] = value_data
                            
                            
                        
                        table_data = df.sort_values(['Date', 'StatusID']).to_dict('records')
                        # print(f'value_data: {value_data}')
                        # print(f'col: {col}')

                        if value_data is not None and value_data != "" and col == "Date":
                            table_data, date_error_open, date_error_msg = dm.date_validation(table_data, data_previous, col, empty = False)

                        if pd.isna(value_data) or value_data == "":
                                df.at[row, col] = ""
                                
    # print(f'date_error_open: {date_error_open}')
    # print(f'date_error_msg: {date_error_msg}')
    # Handle save updates
    elif ctx.triggered_id == 'btn-save-updates-status':
        if n_clicks:
            df = pd.DataFrame(table_data)
            df_prev = pd.DataFrame(data_previous)
            df_original = dm.get_publication_statuses(pub_id=selected_pub_id)
            if not df_prev.empty and df_prev.PubID.unique()[0] == df.PubID.unique()[0]:
                if len(df) == len(df_prev) and not df.equals(df_prev):
                    # Keep the sorted data after deletion
                    if 'Date' in df.columns:
                        df = df.sort_values(['Date', 'StatusID'])
                    table_data = df.to_dict('records')
                    table_data, date_error_open, date_error_msg = dm.date_validation(table_data, df_original.to_dict('records'), ['Date'], empty = False)
                    table_data, date_error_open, date_error_msg = dm.is_null_inserted(table_data, df_original.to_dict('records'), ['Date', 'Sites', 'Devices', 'Languages', 'Genders'])
                    dm.update_status(pub_id=selected_pub_id, new_statuses=table_data)
                    success_open = True
                elif len(df) < len(df_prev):
                    if len(df) > 0:
                        df_prev_filtered = df_prev[df_prev['StatusID'].isin(df['StatusID'])]
                        table_data = df.to_dict('records')
                        data_previous_filtered = df_prev_filtered.to_dict('records')
                        df_original_filtered = df_original[df_original['StatusID'].isin(df['StatusID'])].to_dict('records')
                        table_data, date_error_open, date_error_msg = dm.date_validation(table_data, df_original_filtered, ['Date'], empty = False)
                        table_data, date_error_open, date_error_msg = dm.is_null_inserted(table_data, df_original_filtered, ['Date', 'Sites', 'Devices', 'Languages', 'Genders'])
                        dm.update_status(pub_id=selected_pub_id, new_statuses=table_data)
                        success_open = True
                    elif len(df) == 0:
                        table_data = df.to_dict('records')
                        dm.update_status(pub_id=selected_pub_id, new_statuses=table_data)
                        success_open = True
                elif len(df) == len(df_prev) and df.equals(df_prev):
                    save_error_open = True
                    save_error_msg = "No changes to save"
            else:
                save_error_open = True
                save_error_msg = "No changes to save"
            n_clicks = 0
            
           
                
    if selected_pub_id and table_data:
        # Get dropdown options based on selected publication
        df_data = pd.DataFrame(table_data)
    
        pub_info = df_data.iloc[0]
        if pub_info['Platform'] == 'Hard-coded':
            status_options_list = dd.STATUS_DEVS_FLAG_OPTIONS if pub_info['Feature Flag'] else dd.STATUS_DEVS_NO_FLAG_OPTIONS
        else:  # Retention platform
            status_options_list = dd.STATUS_RETENTION_OPTIONS
        
        # Get current values from the table data if available
        current_sites = set()
        current_devices = set()
        current_genders = set()
        current_languages = set()
        
        if table_data:
            for row in table_data:
                if row.get('Sites'):
                    current_sites.update(row['Sites'].split(', '))
                if row.get('Devices'):
                    current_devices.update(row['Devices'].split(', '))
                if row.get('Genders'):
                    current_genders.update(row['Genders'].split(', '))
                if row.get('Languages'):
                    current_languages.update(row['Languages'].split(', '))
        

        extra_sites = df_data.loc[df_data['Sites'].str.contains(','), 'Sites'].tolist() \
                    # + [update_dropdown[2]] if update_dropdown[0] and update_dropdown[1] == 'Sites' else [] \
                    # + list(current_sites) 
        extra_devices = df_data.loc[df_data['Devices'].str.contains(','), 'Devices'].tolist() \
                    # + [update_dropdown[2]] if update_dropdown[0] and update_dropdown[1] == 'Devices' else [] \
                    # + list(current_devices)
        extra_languages = df_data.loc[df_data['Languages'].str.contains(','), 'Languages'].tolist() \
                    # + [update_dropdown[2]] if update_dropdown[0] and update_dropdown[1] == 'Languages' else [] \
                    # + list(current_languages)
        extra_genders = df_data.loc[df_data['Genders'].str.contains(','), 'Genders'].tolist() \
                    # + [update_dropdown[2]] if update_dropdown[0] and update_dropdown[1] == 'Genders' else [] \
                    # + list(current_genders)

        # Get expanded options using our functions

        expanded_sites = dm.expand_sites_options(pub_info['Planned Sites'], pub_info['Platform'], extra_values=extra_sites    )
        expanded_devices = dm.expand_devices_options(pub_info['Planned Devices'], extra_values=extra_devices)
        expanded_languages = dm.expand_languages_options(pub_info['Planned Languages'], extra_values=extra_languages)
        expanded_genders = dm.expand_genders_options(pub_info['Planned Genders'], extra_values=extra_genders)

        # Create dropdown options
        dropdown = {
                    'Sites': {'options': [{'label': x, 'value': x} for x in expanded_sites]},
                    'Devices': {'options': [{'label': x, 'value': x} for x in expanded_devices]},
                    'Languages': {'options': [{'label': x, 'value': x} for x in expanded_languages]},
                    'Genders': {'options': [{'label': x, 'value': x} for x in expanded_genders]}
        }
           

    print('--------------------------------')

    return table_data, dropdown, date_error_open, date_error_msg, success_open, save_error_open, save_error_msg


# Add callback for table publication info
@callback(
    [Output('table-publication-info-content', 'children'),
     Output('table-publication-info-wrapper', 'style')],
    Input('table-publication-filter', 'value')
)
def update_table_publication_info(selected_pub_id):
    if not selected_pub_id:
        return None, {'display': 'none'}
    
    publications_df = dm.load_publications()
    selected_pub_id = str(selected_pub_id)
    matching_pubs = publications_df[publications_df['PubID'].astype(str) == selected_pub_id]
    
    if matching_pubs.empty:
        return None, {'display': 'none'}
    
    pub_info = matching_pubs.iloc[0]
    
    parameters = ['Name', 'Platform', 'Assignee', 'Start Date', 'Current Status']
    
    if pub_info['Platform'] == 'Hard-coded':
        parameters.append('Feature Flag')
    
    card_content = dm.card_content_insert(parameters, pub_info)
    
    return card_content, {'display': 'block', 'margin-bottom': '20px'}


layout = get_layout()
