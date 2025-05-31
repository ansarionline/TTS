from dash import Dash, html, dcc, clientside_callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_loading_spinners as dls
import sidecanvas as sd
from backend.my import generate_voice
from flask_caching import Cache
import uuid, string, random
from flask import session
from flask import send_from_directory
import warnings
warnings.filterwarnings("ignore")

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG],
        title='AnsariTTS', update_title='AnsariTTS...',
        prevent_initial_callbacks=True)
cache = Cache(app.server, config={"CACHE_TYPE": "simple"})

app.server.secret_key = '49e45ccf3d2653bbaf8eeffc484e90c3146b3'+\
'298cb260618b9f2440eb8f7cbe55d1d6bcd1229b242e3edf800f439c57b735'+\
'317f9556af4855e1443cb7194ad4e4d477433a2e94658abc58d9ce9522b76'+\
'cd0280cb128d0b6d6c0c68ced1c27f8e85b5dcef'
server = app.server
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Textarea(
                            id="main-textarea",
                            placeholder="Enter your text here...",
                            style={'height':'510px'}
                        ),
                        dbc.Spinner(
                            html.Audio(controls=True,
                                    autoPlay=True, 
                                    style={'width':'100%'}, id='aud'),
                            size="sm",
                            color="primary",
                        )
                    ],
                    width=8,
                    style={"align-items":'center'}
                ),
                dbc.Col(
                    sd.make_canvas(),
                    width=4 
                ),
            ],
            align="start", 
            justify="center",
            style={'height':'75vh'}
        ),
        dbc.Toast(
            id='msg-box',
            dismissable=True,
            is_open=False,
            header="Notice",
            icon="primary",
            duration=4000,
            style={
                "position": "fixed",
                "top": 20,
                "right": 20,
                "minWidth": "175px",
                "zIndex": 9999,
            }
        ),

    ],
    fluid=False,
    style={
        "background": "#101010",
        "margin": "50px",
    }
)

@app.server.before_request
def make_session_permanent():
    session.permanent = True
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
@app.server.route('/outputs/<user_id>/<filename>')
def serve_user_audio(user_id, filename):
    return send_from_directory(f'outputs/{user_id}', filename)

sd.register_canvas(app, generate_voice)

if __name__ == '__main__':
    app.run(debug=False)