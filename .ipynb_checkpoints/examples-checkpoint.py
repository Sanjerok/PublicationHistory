from dash import Dash, html, dcc, Input, Output, State

# Initialize the app
app = Dash(__name__)

# Layout
app.layout = html.Div([
    dcc.Input(id='input-text', type='text', placeholder='Enter text here', value=''),  # Text input
    html.Button('Submit', id='submit-button', n_clicks=0),  # Button to trigger the callback
    html.Div(id='output-div')  # Output area
])

# Callback
@app.callback(
    Output('output-div', 'children'),  # Output: Update this div's "children"
    Input('submit-button', 'n_clicks'),  # Input: Number of times the button is clicked
    State('input-text', 'value')        # State: Get the current value of the input
)
def update_output(input_value, n_clicks):
    """
    Updates the output-div only when the button is clicked.
    """
    if len(n_clicks) > 0:  # Ensure the function runs only after the button is clicked
        return f'Button clicked {n_clicks} time(s). You entered: {input_value}'
    return 'Click the button after typing.'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
