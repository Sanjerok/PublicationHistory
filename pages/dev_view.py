import dash
from dash import html, dcc, callback, Input, Output, State, no_update, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import data.data_manipulation as dm
import data.dropdowns as dd
from dash import dash_table
from dash.exceptions import PreventUpdate

# Register the page
dash.register_page(
    __name__,
    path='/dev_view',
    name='Development View'
)

def get_layout():
   

    return html.Div([
        # Filters section
        dbc.Row([
            dbc.Col([
                html.Label("Filter by Platform:"),
                dcc.Dropdown(
                    id='dev-platform-filter',
                    placeholder="Select platform",
                    clearable=True
                )
            ]),
            
            dbc.Col([
                html.Label("Filter by Assignee:"),
                dcc.Dropdown(
                    id='dev-assignee-filter',
                    placeholder="Select assignee",
                    clearable=True
                )
            ]),
             dbc.Col([
                html.Label("Filter by Status:"),
                dcc.Dropdown(
                    id='dev-status-filter',
                    placeholder="Select status",
                    clearable=True
                )
            ]),
            
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                html.Label("Choose Publication:"),
                dcc.Dropdown(
                    id='dev-publication-picker',
                    placeholder="Select publication",
                    clearable=True
                )
            ]),
            
            dbc.Col([
                html.Label("Choose Device:"),
                dcc.Dropdown(
                    id='dev-device-picker',
                    placeholder="Select device",
                    clearable=True
                )
            ])
        ]),

        # Publication Info Card
        html.Div(
            dbc.Card([
                dbc.CardBody(id='dev-publication-info-content')
            ]),
            id='dev-publication-info-wrapper',
            style={'display': 'none', 'margin-bottom': '20px'}
        ),

        # Development Status Table
        html.H2("Development Status"),
        dash_table.DataTable(
            id='dev-status-table',
            columns=[
                {'name': 'Site Group', 'id': 'site_group', 'type': 'text'},
                {'name': 'Site', 'id': 'site', 'type': 'text'},
                {'name': 'Code Deployed', 'id': 'code_deployed', 'type': 'text', 'presentation': 'dropdown'},
                {'name': 'Date of Deployment', 'id': 'deployment_date', 'type': 'text'},
                {'name': 'Feature Flag', 'id': 'feature_flag', 'type': 'text', 'presentation': 'dropdown'},
                {'name': 'Feature Flag Date', 'id': 'feature_flag_date', 'type': 'text'}
            ],
            data=[],
            editable=True,
            style_table={
                'overflowX': 'auto',
                'borderCollapse': 'collapse',
                'minWidth': '100%'
            },
            style_cell={
                'textAlign': 'center',
                # 'padding': '10px',
                'minWidth': '150px',
                'border': '1px solid #ddd',
                'height': '10px',  # Adjust this value
                # 'maxHeight': '20px',  # Should match height
                # 'minHeight': '20px', 
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold',
                'border': '2px solid',
                'textAlign': 'center',
            },
            style_data={
                'whiteSpace': 'normal',
                # 'height': '20px',
                'border': '1px solid #ddd',
                # 'lineHeight': '20px'
            },
            css=[{
                'selector': '.dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table',
                'rule': 'border-collapse: collapse !important;'
            }, {
                'selector': '.dash-spreadsheet-inner td.cell--selected, td.focused',
                'rule': 'background-color: rgba(0, 0, 0, 0.1) !important;'
            }, {
                'selector': 'td.cell--group',
                'rule': '''
                    background-color: rgb(240, 240, 240) !important;
                    vertical-align: middle !important;
                    text-align: center !important;
                    font-weight: bold !important;
                '''
            }, {
                'selector': 'td.cell--group-member',
                'rule': '''
                    border-top: none !important;
                    border-bottom: none !important;
                    background-color: rgb(240, 240, 240) !important;
                '''
            },
            {
                'selector': '.dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner tr',
                'rule': 'height: 10px !important;'
            },
            {
                'selector': '.Select-menu-outer',
                'rule': '''
                    display: block !important;
                    position: absolute;
                    z-index: 1000;
                    background-color: white;
                    max-height: 200px;
                    overflow-y: auto;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                '''
            },
            {
                'selector': '.Select-control',
                'rule': '''
                    cursor: pointer !important;
                    border: 1px solid #ddd !important;
                '''
            },
            {
                        'selector': '.Select-clear',  # Target the clear ("x") button
                        'rule': 'display: none !important;'
                    },
                    {
                        'selector': '.Select-clear-zone',  # Target the clear button zone
                        'rule': 'display: none !important;'
                    }
            ],
            merge_duplicate_headers=True
        ),

        # Save Button
        dbc.Button(
            "Save Updates",
            id="btn-save-dev-updates",
            color="primary",
            className="mt-3 mb-3"
        ),

        # Success Toast
        dbc.Toast(
            id="dev-success-toast",
            header="Success",
            is_open=False,
            duration=4000,
            icon="success",
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

        # Error Toast
        dbc.Toast(
            id="dev-error-toast",
            header="Error",
            is_open=False,
            duration=10000,
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
        
    ])

layout = get_layout()




# Status table filters
@callback(
    [Output('dev-assignee-filter', 'options'),
     Output('dev-status-filter', 'options'),
     Output('dev-publication-picker', 'options'),
     Output('dev-platform-filter', 'options')],
     Output('dev-publication-picker', 'value'),

    [Input('dev-platform-filter', 'value'),
     Input('dev-assignee-filter', 'value'),
     Input('dev-status-filter', 'value')]
    )
def update_table_filters(platform, assignee, status):
    assignee_options, status_options, pub_options, platform_option = [], [], [], []

	
    filtered_pubs_id = dm.get_publication_statuses(platform=platform,
                                                        assignee=assignee,
                                                        status=status).PubID.unique()
	
    publications_df = dm.load_publications()
    filtered_pubs = publications_df[publications_df.PubID.isin(filtered_pubs_id)]


    if platform is not None and platform != '':
        filtered_pubs = filtered_pubs[filtered_pubs['Platform'].fillna('') == platform]
    if assignee is not None and assignee != '':
        filtered_pubs = filtered_pubs[filtered_pubs['Assignee'].fillna('') == assignee]
    if status is not None and status != '':
        filtered_pubs = filtered_pubs[filtered_pubs['Current Status'].fillna('') == status]

    if len(filtered_pubs.PubID.unique()) == 1:
        selected_pub_id = filtered_pubs['PubID'].unique()[0]
    elif len(filtered_pubs.PubID.unique()) > 1:
        selected_pub_id = filtered_pubs['PubID'].unique()
    else:
        selected_pub_id = None

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
        

    return assignee_options, status_options, pub_options, platform_options, selected_pub_id


@callback(
    [Output('dev-publication-info-content', 'children'),
     Output('dev-publication-info-wrapper', 'style')],
    Input('dev-publication-picker', 'value')
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


@callback(
    [Output('dev-status-table', 'data'),
     Output('dev-status-table', 'style_data_conditional'),
     Output('dev-device-picker', 'options'),
     Output('dev-status-table', 'dropdown_conditional')],
    [Input('dev-publication-picker', 'value'),
     Input('dev-device-picker', 'value')]
)
def update_dev_table(publication, device):
    """Update the development status table based on selected publication and device"""
    dropdown_conditional = []

    if True:
        device_options = [{"label":"", "value": ""}]
        # Create empty table with only site groups and sites
        data = []
        
        # Add Staging sites
        data.append({
            'site_group': 'Staging',
            'site': 'StagingCupid'
        })

        # Add Premium CM sites
        premium_sites = sorted(dd.SITE_ELC_SLC_OPTIONS)
        for i, site in enumerate(premium_sites):
            data.append({
                'site_group': 'Premium CM' if i == 1 else '',
                'site': site
            })
        
        # Add Core CM sites (excluding StagingCupid)
        core_sites = sorted([site for site in dd.SITE_CORE_CM_DEVS_OPTIONS if site != 'StagingCupid'])
        for i, site in enumerate(core_sites):
            data.append({
                'site_group': 'Core CM' if i == 0 else '',
                'site': site
            })
            
        
        # Style conditions for the table
        style_conditional = []
        
        # Style for site_group column
        style_conditional.extend([
            # Style for cells with group labels
            {
                'if': {
                    'column_id': 'site_group',
                    'filter_query': '{site_group} = "Staging" or {site_group} = "Premium CM"'
                },
                'backgroundColor': 'rgb(240, 240, 240)',
                'fontWeight': 'bold',
                'textAlign': 'center',
                'borderTop': '2px solid',
                'borderBottom': '2px solid',
                'borderLeft': '2px solid',
                'borderRight': '2px solid'
            },
            # Style for empty cells in the group
            {
                'if': {
                    'column_id': 'site_group',
                    'filter_query': '{site_group} = "" or {site_group} = "Core CM"'
                },
                'backgroundColor': 'rgb(240, 240, 240)',
                'fontWeight': 'bold',
                'textAlign': 'center',
                'borderTop': 'none',
                'borderBottom': 'none',
                'borderLeft': '2px solid',
                'borderRight': '2px solid'
            }
            , {
                'if': {
                    'row_index': 0,
                },
                'borderTop': '2px solid',
                # 'borderBottom': '2px solid',
             
            }
            , {
                'if': {
                    'row_index': len(data) - 1,
                },
                # 'borderTop': '2px solid',
                'borderBottom': '2px solid',
             
            }
            , {
                'if': {
                    'column_id': 'feature_flag_date',
                },
                # 'borderTop': '2px solid',
                'borderRight': '2px solid',
             
            },
            {
                'if': {
                    'column_id': 'site',
                },
                'borderRight': '1px solid ',
            }
            ,
            {
                'if': {
                    'column_id': 'feature_flag',
                },
                'borderLeft': '1px solid ',
            },
            {
                'if': {
                    'row_index': [0, 2],
                },
                'borderBottom': '2px solid',
               
            },
            {
                'if': {
                    'column_id': 'site',
                },
                'textAlign': 'left',
                'paddingLeft': '10px',
                'fontSize': '13px',
            },
           
        ])

            # Add these style conditions for "Excluded" cells
        style_conditional.extend([
            {
                'if': {
                    'filter_query': '{code_deployed} eq "Excluded"',
                    'column_id': 'code_deployed'
                },
                'backgroundColor': '#f0f0f0',
                'color': '#666666',
                'cursor': 'not-allowed',
                'pointerEvents': 'none'
            },
            {
                'if': {
                    'filter_query': '{deployment_date} eq "Excluded"',
                    'column_id': 'deployment_date'
                },
                'backgroundColor': '#f0f0f0',
                'color': '#666666',
                'cursor': 'not-allowed',
                'pointerEvents': 'none'
            },
            {
                'if': {
                    'filter_query': '{feature_flag} eq "Excluded"',
                    'column_id': 'feature_flag'
                },
                'backgroundColor': '#f0f0f0',
                'color': '#666666',
                'cursor': 'not-allowed',
                'pointerEvents': 'none'
            },
            {
                'if': {
                    'filter_query': '{feature_flag_date} eq "Excluded"',
                    'column_id': 'feature_flag_date'
                },
                'backgroundColor': '#f0f0f0',
                'color': '#666666',
                'cursor': 'not-allowed',
                'pointerEvents': 'none'
            },
            {
                'if': {
                    'column_id': 'site',
                },
                'backgroundColor': '#f0f0f0',
                'color': '#666666',
                'cursor': 'not-allowed',
                'pointerEvents': 'none'
            }
            , {
                'if': {
                    'column_id': 'site_group',
                },
                'backgroundColor': '#f0f0f0',
                'color': '#666666',
                'cursor': 'not-allowed',
                'pointerEvents': 'none'
            }
        ])
    if not publication or not device:
        pass

    if publication and not device:
        publications_df = dm.load_publications()
        pub_details = publications_df[publications_df['PubID'] == int(publication)].iloc[0]
        device_list = dm.expand_devices_options(pub_details['Planned Devices'])
        device_options = [{'label': x, 'value': x} for x in device_list] or [{'label': 'No options available', 'value': ''}]
    
    if publication and device:
        data = dm.get_site_statuses(publication, device, data)

        publications_df = dm.load_publications()
        pub_details = publications_df[publications_df['PubID'] == int(publication)].iloc[0]
        has_feature_flag = pub_details['Feature Flag'] if pub_details['Feature Flag'] == 'True' else False
        device_options = [{'label': x, 'value': x} for x in dm.expand_devices_options(pub_details['Planned Devices'])] or [{'label': 'No options available', 'value': ''}]
        if not has_feature_flag:
            style_conditional.extend([
                {
                    'if': {'column_id': col},
                    'backgroundColor': '#f0f0f0',
                    'color': '#666666'
                } for col in ['feature_flag', 'feature_flag_date']
            ])

        dropdown_conditional = [{
        
                    "if": {
                            'column_id': 'feature_flag',
                            'filter_query': '{feature_flag} eq "Excluded"'
                    },
                    
                "options": [{'label': "Excluded", 'value': "Excluded"}]
            },
            {
                "if": {
                        'column_id': 'feature_flag',
                        'filter_query': '{feature_flag} eq "True" or {feature_flag} eq "False"'
                },
                
               "options": [{'label': "True", 'value': "True"}, {'label': "False", 'value': "False"}]
            }
            , {
        
                    "if": {
                            'column_id': 'feature_flag_date',
                            'filter_query': '{feature_flag_date} eq "Excluded"'
                    },
                    
                "options": [{'label': "Excluded", 'value': "Excluded"}]
            }
            , {
        
                    "if": {
                            'column_id': 'deployment_date',
                            'filter_query': '{deployment_date} eq "Excluded"'
                    },
                    
                "options": [{'label': "Excluded", 'value': "Excluded"}]
            },
            {
                "if": {
                        'column_id': 'code_deployed',
                        'filter_query': '{code_deployed} eq "Excluded"'
                },
                
               "options": [{'label': "Excluded", 'value': "Excluded"}]
            },
            {
                "if": {
                        'column_id': 'code_deployed',
                        'filter_query': '{code_deployed} eq "True" or {code_deployed} eq "False"'
                },
                
               "options": [{'label': "True", 'value': "True"}, {'label': "False", 'value': "False"}]
            }

            ]
     
        

    return data, style_conditional, device_options, dropdown_conditional

@callback(
    [Output('dev-success-toast', 'is_open'),
     Output('dev-success-toast', 'children'),
     Output('dev-error-toast', 'is_open'),
     Output('dev-error-toast', 'children'),
     Output('btn-save-dev-updates', 'n_clicks'),
     Output('dev-status-table', 'data', allow_duplicate=True)],
    Input('btn-save-dev-updates', 'n_clicks'),
    [Input('dev-status-table', 'data'),
     Input('dev-status-table', 'data_previous'),
     State('dev-publication-picker', 'value'),
     State('dev-device-picker', 'value')]
     , prevent_initial_call=True
)


def dev_table_updates(n_clicks, data, data_previous, publication, device):

    def add_new_status(new_statuses, Publication, max_status_id, action, date, sites, devices):
        new_statuses.append(
                {
                'PubID': int(Publication),
                'StatusID': max_status_id + 1,
                "Action": action,
                "Date": date,
                "Sites": sites,
                "Devices": devices,
                "Genders":"All",
                "Languages":"All",
                "Comment": f"Changes added from dev view at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                }
            )
        max_status_id += 1
        return pd.DataFrame(new_statuses).drop_duplicates().to_dict('records'), max_status_id
    

    triggered = ctx.triggered_id

    is_success_popup, is_error_popup = False, False
    success_msg = ""
    error_msg = []

    publications_df = dm.load_publications()
    if publication:
        pub_info = publications_df[publications_df.PubID == int(publication)]

    if triggered == 'dev-status-table' and data_previous:
         df = pd.DataFrame(data).fillna('') if data else pd.DataFrame()
         df_prev = pd.DataFrame(data_previous).fillna('')
         
         if df.shape == df_prev.shape:
            difference = df != df_prev
            diff_indices = difference.stack()[difference.stack()].index
           
            if len(diff_indices) == 1:
                row, col = diff_indices[0]
                value_data = df.at[row, col]
                value_data_previous = df_prev.at[row, col]

                if value_data is not None and value_data != "" and col in ('feature_flag_date', 'deployment_date'):
                    data, is_error_popup, msg = dm.date_validation(data, data_previous, col)
                    error_msg.append(msg)
         else:
             is_error_popup = True
             error_msg.append("The shape of the table is different!")
    
    if triggered == 'btn-save-dev-updates' and n_clicks and publication and device and data_previous:
        n_clicks = 0
        original_data, _, _, _ = update_dev_table(publication, device)
        df = pd.DataFrame(data).fillna('')
        df_prev = pd.DataFrame(original_data).fillna('')
        
        
        difference = df != df_prev
        # print(f'difference: {difference}')
        diff_indices = difference.stack()[difference.stack()].index

        if len(diff_indices) == 0:
            is_error_popup = True
            error_msg.append("No changes to save")
       

        elif len(diff_indices) > 0:
            statuses_df = dm.load_statuses()
            
            pub_statuses = statuses_df[statuses_df['PubID'] == int(publication)]
            update_lst = []
            data, is_error_popup, msg = dm.date_validation(data, original_data, ['feature_flag_date', 'deployment_date'])
            print(f'is_error_popup: {is_error_popup}')
            error_msg.append(msg)
        
            for row, col in diff_indices:
                code_deployed = df.at[row, 'code_deployed']
                code_deployed_date = df.at[row, 'deployment_date']
                feature_flag = df.at[row, 'feature_flag']
                feature_flag_date = df.at[row, 'feature_flag_date']
    
                if  df.at[row, 'code_deployed'] == 'False' and df.at[row, 'feature_flag'] == 'True':
                    is_error_popup = True
                    error_msg.append(f"Site: {df.at[row, 'site']}. Feature Flag cannot be on without Code Deployed. ")

                # if   df.at[row, 'feature_flag'] == 'False' and (df.at[row, 'feature_flag_date'] is not  None and df.at[row, 'feature_flag_date'] != ''):
                #     is_error_popup = True
                #     error_msg.append(f"Site: {df.at[row, 'site']}. You inputed Feature Flag Date, but Feature flag is turned off.")

                
                if   df.at[row, 'feature_flag'] == 'True' and (df.at[row, 'feature_flag_date'] is  None or df.at[row, 'feature_flag_date'] == ''):
                    is_error_popup = True
                    error_msg.append(f"Site: {df.at[row, 'site']}. You inputed Feature Flag, but Feature flag Date is empty.")

                if   df.at[row, 'feature_flag'] == 'True' and df.at[row, 'code_deployed'] == 'True' and (df.at[row, 'feature_flag_date'] is  None or df.at[row, 'feature_flag_date'] == '') and (df.at[row, 'deployment_date'] is  None or df.at[row, 'deployment_date'] == '') and df.at[row, 'deployment_date'] > df.at[row, 'feature_flag_date']:
                    is_error_popup = True
                    error_msg.append(f"Site: {df.at[row, 'site']}. The feature flag date cannot be before the code deployed date.")

                # if   df.at[row, 'code_deployed'] == 'False' and (df.at[row, 'deployment_date'] is not None and df.at[row, 'deployment_date'] != ''):
                #     is_error_popup = True
                #     error_msg.append(f"Site: {df.at[row, 'site']}. You inputed Code Deployed Date, but Code Deployed is turned off.")

                if   df.at[row, 'code_deployed'] == 'True' and (df.at[row, 'deployment_date'] is  None or df.at[row, 'deployment_date'] == ''):
                    is_error_popup = True
                    error_msg.append(f"Site: {df.at[row, 'site']}. You inputed Code Deployed, but Code Deployed Date is empty.")

                update_lst.append(
                    {
                    'PubID': int(publication),
                    'Device': device,
                    'Site': df.at[row, 'site'],
                    'Code Deployed': code_deployed,
                    'Feature Flag': feature_flag,
                    'Deployment Date': code_deployed_date,
                    'Feature Flag Date': feature_flag_date,
                    'Previous Code Deployed': df_prev.at[row, 'code_deployed'],
                    'Previous Feature Flag': df_prev.at[row, 'feature_flag'],
                    'Previous Deployment Date': df_prev.at[row, 'deployment_date'],
                    'Previous Feature Flag Date': df_prev.at[row, 'feature_flag_date']
                    }
                )
                df_updates = pd.DataFrame(update_lst)
                df_grouped = df_updates.groupby(['PubID', 'Device', 'Code Deployed', 'Feature Flag', 'Deployment Date', 'Feature Flag Date', 'Previous Code Deployed', 'Previous Feature Flag', 'Previous Deployment Date', 'Previous Feature Flag Date']).Site.apply(lambda x: ', '.join(list(set(x)))).reset_index()
                print(f'df_grouped: {df_grouped}')
                max_status_id = pub_statuses['StatusID'].max()
                new_statuses = []

                

                if not is_error_popup:
                    for i in df_grouped.index:
                        print(f'grouped.iloc[i]: {df_grouped.iloc[i]}')
                        feature_flag = df_grouped.at[i, 'Feature Flag']
                        feature_flag_previous = df_grouped.at[i, 'Previous Feature Flag']
                        code_deployed = df_grouped.at[i, 'Code Deployed']
                        code_deployed_previous = df_grouped.at[i, 'Previous Code Deployed']
                        feature_flag_date = df_grouped.at[i, 'Feature Flag Date']
                        feature_flag_date_previous = df_grouped.at[i, 'Previous Feature Flag Date']
                        deployment_date = df_grouped.at[i, 'Deployment Date']
                        deployment_date_previous = df_grouped.at[i, 'Previous Deployment Date']

                        feature_flag_change = feature_flag != feature_flag_previous 
                        code_deployed_change = code_deployed != code_deployed_previous 
                        print(f'feature_flag_change: {feature_flag_change}')
                        print(f'code_deployed_change: {code_deployed_change}')
                        if code_deployed_change and feature_flag_change:
                            print('code_deployed_change and feature_flag_change')
                            if code_deployed_previous == 'False' and feature_flag_previous == 'False':
                                print('not code_deployed_previous and not feature_flag_previous')
                                new_statuses, max_status_id  = add_new_status( new_statuses
                                                                        , publication
                                                                        , max_status_id
                                                                        , 'Deployed'
                                                                        , df_grouped.at[i, 'Deployment Date']
                                                                        , df_grouped.at[i, 'Site']
                                                                        , df_grouped.at[i, 'Device'])

                                new_statuses, max_status_id  = add_new_status(new_statuses
                                                                        , publication
                                                                        , max_status_id
                                                                        , 'Roll Out'
                                                                        , df_grouped.at[i, 'Feature Flag Date']
                                                                        , df_grouped.at[i, 'Site']
                                                                        , df_grouped.at[i, 'Device'])
                            elif code_deployed_previous == 'True':
                                print('code_deployed_previous')
                                new_statuses, max_status_id  = add_new_status(new_statuses
                                                                , publication
                                                                , max_status_id
                                                                , 'Roll Back'
                                                                , df_grouped.at[i, 'Deployment Date']
                                                                , df_grouped.at[i, 'Site']
                                                                , df_grouped.at[i, 'Device'])
                            else:
                                print('Something else')
                                

                        elif code_deployed_change and not feature_flag_change:
                            print('code_deployed_change and not feature_flag_change')
                            if code_deployed_previous == 'False':
                                print('not code_deployed_previous')
                                print(f'pub_info: {pub_info}')
                                print(f'pub_info.Platform: {pub_info.Platform}')
                                new_statuses, max_status_id  = add_new_status(new_statuses
                                                                        , publication
                                                                        , max_status_id
                                                                        , 'Deployed' if pub_info.Platform.iloc[0] == 'Hard-coded' else "Expanded"
                                                                        , df_grouped.at[i, 'Deployment Date']
                                                                        , df_grouped.at[i, 'Site']
                                                                        , df_grouped.at[i, 'Device'])
                        
                            elif code_deployed_previous == 'True':
                                print('code_deployed_previous')
                                new_statuses, max_status_id  = add_new_status(new_statuses
                                                                        , publication
                                                                        , max_status_id
                                                                        , 'Roll Back'
                                                                        , df_grouped.at[i, 'Deployment Date']
                                                                        , df_grouped.at[i, 'Site']
                                                                        , df_grouped.at[i, 'Device'])
                            else:
                                print('Something else')
                                
                        elif not code_deployed_change and feature_flag_change:
                            print('not code_deployed_change and feature_flag_change')
                            if feature_flag_previous == 'False':
                                print('not feature_flag_previous')
                                new_statuses, max_status_id  = add_new_status(new_statuses
                                                                        , publication
                                                                        , max_status_id
                                                                        , 'Feature flag on'
                                                                        , df_grouped.at[i, 'Feature Flag Date']
                                                                        , df_grouped.at[i, 'Site']
                                                                        , df_grouped.at[i, 'Device'])                    
                            
                            elif feature_flag_previous == 'True':
                                print('feature_flag_previous')
                                new_statuses, max_status_id  = add_new_status(new_statuses
                                                                        , publication
                                                                        , max_status_id
                                                                        , 'Roll Back'
                                                                        , df_grouped.at[i, 'Feature Flag Date']
                                                                        , df_grouped.at[i, 'Site']
                                                                        , df_grouped.at[i, 'Device'])	
                            else:
                                print('Something else')
                                
                        else:
                            print('else')
                                    
                    dm.update_status(pub_id=int(publication), new_statuses=new_statuses, dev_view=True)
                    is_success_popup = True
                    success_msg = 'Changes saved successfully!'
                




    elif triggered == 'btn-save-dev-updates' and n_clicks  and (not publication or not device):
        is_error_popup = True
        error_msg.append("Please select a publication and device. No data to save.")
    elif triggered == 'btn-save-dev-updates' and n_clicks and not data_previous:
        is_error_popup = True
        error_msg.append("No data to save.")
            

    error_msg = [html.P([i, html.Br()]) if i != error_msg[0] else i for i in error_msg]
    print('--------------------------------')
    return is_success_popup, success_msg, is_error_popup, error_msg, n_clicks, data


