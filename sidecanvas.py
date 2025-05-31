from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import dash_daq as daq
import random, uuid
import string, base64
import threading
from flask import session
import time
import threading
import shutil

cleanup_timers = {}

def schedule_cleanup(user_id, folder_path, delay=1800):
    if user_id in cleanup_timers:
        timer = cleanup_timers[user_id]
        timer.cancel()
    def cleanup():
        try:
            shutil.rmtree(folder_path)
            print(f"Deleted folder: {folder_path}")
        except Exception as e:
            print(f"Cleanup error for {folder_path}: {e}")
        cleanup_timers.pop(user_id, None)
    timer = threading.Timer(delay, cleanup)
    timer.daemon = True
    timer.start()
    cleanup_timers[user_id] = timer

def generate_captcha(length=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def random_captcha_spans(code):
    spans = []
    for c in code:
        rot = random.randint(-25, 25)
        skew = random.randint(-25, 25)
        style = {
            "display": "inline-block",
            "transform": f"rotate({rot}deg) skewY({skew}deg)",
            "fontWeight": "bold",
            "color": "#00ffd0",
            "textShadow": "1px 1px 2px #000, 0 0 6px #00e0ff88",
            "margin": "0 2px"
        }
        spans.append(html.Span(c, style=style))
    return spans

def giveinptbtn(txt, btn, **kwargs):
    return dbc.InputGroup(
        [
            dbc.InputGroupText(
                txt,
                style={
                    "min-width": "120px",
                    "margin": "0",
                    "display": "flex",
                    "alignItems": "center",
                    "height": "38px"
                }
            ),
            dcc.Upload(
                dbc.Button(
                    btn,
                    id=btn.replace(' ', '-').lower(),
                    class_name="w-100",
                    style={
                        "margin": "0",
                        "height": "38px"
                    },
                    **kwargs
                ),
                id='upld-ref',
                style={"width": "100%", "margin": "0"}
            ),
        ],
        style={
            "width": "100%",
            "margin-bottom": "21px",
            "alignItems": "center",
            "display": "flex",
            'gap':'10px'
        }
    )

def giveinptslct(txt, opt, **kwargs):
    return dbc.InputGroup(
        [
            dbc.InputGroupText(txt, style={"minWidth": "120px", 'margin-bottom':'3px'}),
            dbc.Select(opt, id=txt.replace(' ', '-').lower(), class_name="w-80",
                    **kwargs),
        ],
        style={"width": "100%", 'margin-bottom':'21px', 'gap':'10px'}
    )
def giveinptprgs(txt, **kwargs):
    return dbc.InputGroup(
        [
            dbc.InputGroupText(txt, style={"minWidth": "120px", 'margin-bottom':'3px'}),
            daq.Slider(**kwargs)
        ],
        style={
            "width": "100%",
            "alignItems": "center",
            "display": "flex",
            "margin-bottom":'21px',
            'gap':'10px'
            })

code = generate_captcha(5)
code_i = random_captcha_spans(code)
def make_canvas():
    cnvs = dbc.Container([
            giveinptbtn('Voice', '📂 Load Reference'),
            giveinptslct('Language',  ['English'], value='English'),
            giveinptslct('Emotion',    ['Default', 'Excited', 'Cheerful', 'Sad', 'Angry'], value='Default'),
            giveinptprgs(
                'Speed',
                id='spd-slider',
                min=0.0,
                max=2.0,
                step=0.1,
                value=1.0,
                marks=None
            ),
            giveinptprgs(
                'Volume',
                id='vol-slider',
                min=0.0,
                max=2.0,
                step=0.1,
                value=1.0,
                marks=None
            ),
            giveinptprgs(
                'Pitch',
                id='pch-slider',
                min=0.0,
                max=2.0,
                step=0.1,
                value=1.0,
                marks=None
            ),
            html.Div([
                dbc.InputGroup(
                    [
                        dbc.Input(id='captcha-inpt', required=True, placeholder='Enter Code...',
                                maxlength=5),
                        dbc.Spinner(dbc.InputGroupText(id='captcha-code', style={
                            'height':'70px'
                        }, children=code_i), 
                            size="sm",
                            color="primary"
                            )
                    ],
                    style={
                        'margin-bottom': '21px',
                        'height':'70px'
                    }
                ),
            ], style={'margin-bottom': '12px'}),
                        dbc.Spinner(dbc.Button('⚡️ Generate', id='gen-btn', 
                                    class_name="w-100",
                                    style={'margin-bottom':'21px',
                                        'border-radius':'20px'},
                                    disabled=True), 
                                    size="sm",
                                    color="primary"
                            ),
            dcc.Download(id='dnld-wav'),
                        dbc.Spinner(dbc.Button('💾 Export', id='exprt-btn', 
                                    class_name="w-100",
                                    style={'margin-bottom':'21px',
                                        'border-radius':'20px'},
                                    disabled=True), 
                                    size="sm",
                                    color="primary"
                            ),
        dcc.Store(id='captcha-stor', data=code),
    ], style={'padding':'2px'})
    return cnvs

def permission(app):
    @app.callback(
        Output('captcha-stor', 'data'    , allow_duplicate=True),
        Output('captcha-inpt', 'value'   , allow_duplicate=True),
        Output('captcha-code', 'children', allow_duplicate=True),
        Output('gen-btn'     , 'disabled', allow_duplicate=True),
        Input ('captcha-inpt', 'n_submit'),
        State ('captcha-inpt', 'value'   ),
        State ('captcha-stor', 'data'    ),
        prevent_initial_callbacks=True
    )
    def do(n, inpt, corr):
        code = generate_captcha(5)
        code_span = random_captcha_spans(code)
        return code, '', code_span, not inpt.upper() == corr.upper()

def generate(app, tts):
    @app.callback(
        Output('exprt-btn', 'disabled',    allow_duplicate=True),
        Output('aud', 'src',    allow_duplicate=True),
        Output('gen-btn', 'disabled',      allow_duplicate=True),
        Output('captcha-stor', 'data'    , allow_duplicate=True),
        Output('captcha-inpt', 'value'   , allow_duplicate=True),
        Output('captcha-code', 'children', allow_duplicate=True),
        Input ('gen-btn'  , 'n_clicks'),
        State ('main-textarea', 'value'),
        State ('emotion', 'value')
    )
    def do(n_clicks, text, emotion):
        time_i = time.perf_counter()
        code = generate_captcha(5)
        code_span = random_captcha_spans(code)
        if not n_clicks:
            return no_update
        try:
            id_ = session['user_id']
            tts(text = text, speaker_tone = emotion.lower().strip(),
                filename = id_ + '-output.wav', tmp_dir = f"outputs/{session['user_id']}")
            print("Done")
            time_f = time.perf_counter()
            schedule_cleanup(session['user_id'],  f"outputs/{session['user_id']}", delay=900)
            print(f"Time taken for the audio with character {len(text)} is {time_f - time_i} sec.")
            return False, f'/outputs/{session["user_id"]}/{id_}-output.wav', True, code, '', code_span
        except Exception as e:
            print(e)
            return True, '', True, code, '', code_span

def register_canvas(app, tts):
    permission(app)
    generate(app, tts)


