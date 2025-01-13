from re import I
import dash
from dash import html, dcc, callback, Input, Output, State, no_update, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import data.data_manipulation as dm
# from pages.dev_view import update_dev_table as get_statuses
import data.dropdowns as dd
from dash import dash_table
from dash.exceptions import PreventUpdate

# Register the page
dash.register_page(
    __name__,
    path='/ret_view',
    name='Retention View'
)

def get_layout():
    columns = [
                {'name': 'Publication', 'id': 'Publication', 'type': 'text', "presentation": "markdown"},              
                {'name': 'Sites', 'id': 'Sites', 'type': 'text'},              
               
            ] + [{'name': val, 'id': val, 'type': 'text'} for val in sorted(dd.SITE_CORE_CM_RETENTION_OPTIONS) + sorted(dd.SITE_ELC_SLC_OPTIONS)]
    # print(f'columns: {columns}')

    return html.Div([
        # Filters section
        dbc.Row([
            dbc.Col([
                html.Label("Filter by Platform:"),
                dcc.Dropdown(
                    id='ret-platform-filter',
                    placeholder="Select platform",
                    clearable=True,
                    
                )
            ]), 
            
            dbc.Col([
                html.Label("Filter by Assignee:"),
                dcc.Dropdown(
                    id='ret-assignee-filter',
                    placeholder="Select assignee",
                    clearable=True
                )
            ]),
             dbc.Col([
                html.Label("Filter by Status:"),
                dcc.Dropdown(
                    id='ret-status-filter',
                    placeholder="Select statuts",
                    clearable=True
                )
            ]),
            
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                html.Label("Choose Publication:"),
                dcc.Dropdown(
                    id='ret-publication-picker',
                    placeholder="Select publication",
                    clearable=True,
                    multi=True
                )
            ]),
            
        ]),

        dbc.Row([
            dbc.Col([
                html.Label("Choose Device:"),
                dcc.Dropdown(
                    id='ret-device-picker',
                    placeholder="Select device",
                    clearable=True,
                    multi =True
                )
            ]),
            # dbc.Col([
            #     html.Label("Choose Language:"),
            #     dcc.Dropdown(
            #         id='ret-language-picker',
            #         placeholder="Select language",
            #         clearable=True,
            #         multi=True
            #     )
            # ]),
            # dbc.Col([
            #     html.Label("Choose Gender:"),
            #     dcc.Dropdown(
            #         id='ret-gender-picker',
            #         placeholder="Select gender",
            #         clearable=True,
            #         multi = True
            #     )
            # ]),
            dbc.Col([
                html.Label("Analytics:"),
                dcc.Dropdown(
                    id='ret-analytics-picker',
                    # placeholder=",
                    clearable=True,
                    multi=True
                )
            ]),
            dbc.Col([
                html.Label("Mode"),
                dcc.Dropdown(
                    id='ret-mode-picker',
                    # placeholder="Select device",
                    # clearable=True
                    value = 'Info',
                    options = [{'label': val, 'value': val} for val in ['Info', 'Expand', 'Roll back', 'Restart']]
                )
            ]),

        ]),
  

        # Publication Info Card
   	 dbc.Row([
            dbc.Col([
                html.Label("Check Publication details:"),
                dcc.Dropdown(
                    id='ret-publication-card-picker',
                    placeholder="Select publication",
                    clearable=True,
                )
            ]),
            
        ]),
        html.Div(
            dbc.Card([
                dbc.CardBody(id='ret-publication-info-content')
            ]),
            id='ret-publication-info-wrapper',
            style={'display': 'none', 'margin-bottom': '20px'}
        ),
        
        # Retention Status Table
        html.H2("Development Status"),
        dash_table.DataTable(
            id='ret-status-table',
            columns=columns,
            data=[],
            editable=True
            , style_table={
                'overflowX': 'auto',
                'borderCollapse': 'collapse',
                'minWidth': '100%'
            }
            , style_cell={
                'textAlign': 'center',
                # 'padding': '10px',
                'minWidth': '150px',
                # 'border': '1px solid #ddd',
                'height': '10px',  # Adjust this value
                # 'maxHeight': '20px',  # Should match height
                # 'minHeight': '20px', 
            }
            # style_header={
            #     'backgroundColor': 'rgb(230, 230, 230)',
            #     'fontWeight': 'bold',
            #     'border': '2px solid',
            #     'textAlign': 'center',
            # },
            # style_data={
            #     'whiteSpace': 'normal',
            #     # 'height': '20px',
            #     'border': '1px solid #ddd',
            #     # 'lineHeight': '20px'
            # }
            , css=[      
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
          
            ],
            merge_duplicate_headers=True
        ),

        # Save Button
        dbc.Button(
            "Save Updates",
            id="btn-save-ret-updates",
            color="primary",
            className="mt-3 mb-3"
        ),

        # Success Toast
        dbc.Toast(
            id="ret-success-toast",
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
            id="ret-error-toast",
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
        
    ],
            className='mb-3')

layout = get_layout()




# Status table filters
@callback(
    [Output('ret-assignee-filter', 'options'),
     Output('ret-status-filter', 'options'),
     Output('ret-publication-picker', 'options'),
     Output('ret-platform-filter', 'options'),
     Output('ret-publication-picker', 'value')
     ],

    [Input('ret-platform-filter', 'value'),
     Input('ret-assignee-filter', 'value'),
     Input('ret-status-filter', 'value'),
     Input('ret-publication-picker', 'value'),
     Input('ret-publication-picker', 'options')
     ]
    )

def update_retention_table_filters(platform, assignee, status, publication, pub_options):
	
    publications_df = dm.load_publications()
    filtered_pubs = publications_df.copy()
    if pub_options is not None and pub_options != []:
        old_pub_options = pub_options[:]
    else:
        old_pub_options = []

    


    if platform is not None and platform != '':
        filtered_pubs = filtered_pubs[filtered_pubs['Platform'] == platform]
    if assignee is not None and assignee != '':
        filtered_pubs = filtered_pubs[filtered_pubs['Assignee'] == assignee]
    if status is not None and status != '':
        filtered_pubs = filtered_pubs[filtered_pubs['Current Status'] == status]
        # print(f'status  : {status}')

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
    # print(f'Inner publication: {publication}')
    platform_options = [
        {'label': x, 'value': x} 
        for x in sorted(filtered_pubs['Platform'].unique())
    ] or [{'label': 'No options available', 'value': ''}]
    
    if publication is not None and publication != []:
        if 'All' in publication:
            publication.extend([i['value'] for i in old_pub_options])
        # print(publication)
        publication =list(map(int, [i for i in publication if i != 'All']))
        pub_options += [{'label': f"{row['Name']} (ID: {row['PubID']})", 'value': str(row['PubID'])} for _, row in publications_df[publications_df['PubID'].isin(publication)].drop_duplicates().iterrows()]
        publication =list(set(map(str, [i for i in publication if i != 'All'])))
        publication.sort(key=lambda i: int(i))
    
    if len(pub_options) > 0:
        pub_options.sort(key=lambda i: int(i['value']))
        pub_options = [{'label': "All", "value": 'All'}] + pub_options

    
    
    
    # print(f'Outer publication: {publication}')
    return assignee_options, status_options, pub_options, platform_options, publication

@callback(
    Output('ret-publication-card-picker', 'options'),
    Input('ret-publication-picker', 'value')
)
def update_publication_card_picker(publication_lst):
    publications_df = dm.load_publications()
    publications_df['PubID'] = publications_df['PubID'].astype(str)
    if publication_lst is not None and publication_lst != []:
       publication_lst = list(map(str, publication_lst))
    else:
        publication_lst = []
    
    publications_df = publications_df[publications_df['PubID'].isin(publication_lst)]

    

    pub_options = [
        {'label': f"{row['Name']} (ID: {row['PubID']})", 'value': str(row['PubID'])}
        for _, row in publications_df[['Name', 'PubID']].drop_duplicates().iterrows()
    ] or [{'label': 'No options available', 'value': ''}]
    return pub_options

@callback(
    [Output('ret-publication-info-content', 'children'),
     Output('ret-publication-info-wrapper', 'style')],
    Input('ret-publication-card-picker', 'value')
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
    
    parameters = ['Name', 'Platform', 'Assignee', 'Start Date', 'Current Status', 'Sites', 'Devices', 'Languages', 'Genders', 'Analytics']
    
    if pub_info['Platform'] == 'Hard-coded':
        parameters.append('Feature Flag')
    
    card_content = dm.card_content_insert(parameters, pub_info)
    
    return card_content, {'display': 'block', 'margin-bottom': '20px'}




@callback(
    Output('ret-status-table', 'data'),
     Output('ret-status-table', 'style_data_conditional'),
     Output('ret-device-picker', 'options'),
    #  Output('ret-language-picker', 'options'),
    #  Output('ret-gender-picker', 'options'),
     Output('ret-analytics-picker', 'options'),
    #  Output('ret-status-table', 'dropdown_conditional'),
    [Input('ret-publication-picker', 'value'),
     Input('ret-device-picker', 'value'),
    #  Input('ret-language-picker', 'value'),
    #  Input('ret-gender-picker', 'value'),
     Input('ret-analytics-picker', 'value')]
)
def update_ret_table(publications, device, analytics):


    if True:
        publications_df = dm.load_publications()
        device_options = [{"label":"", "value": ""}]
        # language_options = [{"label":"", "value": ""}]
        # gender_options = [{"label":"", "value": ""}]
        analytics_options = [{"label":"", "value": ""}]

        data = []
        if publications is None or publications == []:
            publications = []

        for publication in publications:
            if publication != 'All':
                data.append({'Publication': publications_df[publications_df['PubID'] == int(publication)].iloc[0]['Publication']})
        
        # Style conditions for the table
        style_conditional = []
            # Add these style conditions for "Excluded" cells
        style_conditional.extend([
             {
                'if': {
                    'column_id': 'Publication',
                },
                'backgroundColor': '#f0f0f0',
                'color': '#666666',
                'cursor': 'not-allowed',
                # 'pointerEvents': 'none'
            }
        ])


    if publications is not None and publications != []:

        # get dropdowns
        publications_df = dm.load_publications()
        pubs_details = publications_df[publications_df['PubID'].isin(list(map(int, publications)))]
        device_list = []
        # language_list = []
        # gender_list = []
        analytics_list = []
        for publication in publications:
            print(publication)
            device_list.extend(dm.expand_devices_options(pubs_details.loc[(pubs_details.PubID == int(publication)), 'Planned Devices'].iloc[0]))
            # language_list.extend(dm.expand_languages_options(pubs_details.loc[(pubs_details.PubID == int(publication)), 'Planned Languages'].iloc[0]))
            # gender_list.extend(dm.expand_genders_options(pubs_details.loc[(pubs_details.PubID == int(publication)), 'Planned Genders'].iloc[0]))
            analytics_list.append(pubs_details.loc[(pubs_details.PubID == int(publication)), 'Analytics'].iloc[0])
            # print(analytics_list)

        device_list = dm.expand_devices_options(', '.join(set(device_list)))
        # language_list = dm.expand_languages_options(', '.join(set(language_list)))
        # gender_list = dm.expand_genders_options(', '.join(set(gender_list)))
        analytics_list = [i for i in set(analytics_list) if i != '']
        analytics_list.sort()

        device_options = [{'label': x, 'value': x} for x in device_list] or [{'label': 'No options available', 'value': ''}]
        # language_options = [{'label': x, 'value': x} for x in language_list] or [{'label': 'No options available', 'value': ''}]
        # gender_options = [{'label': x, 'value': x} for x in gender_list] or [{'label': 'No options available', 'value': ''}]
        analytics_options = [{'label': x, 'value': x} for x in analytics_list] or [{'label': 'No options available', 'value': ''}]
    
    
        if device is None:
            device = []
            
        

    return data, style_conditional, device_options, analytics_options



