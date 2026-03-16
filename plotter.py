# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = [
#     "pandas",
#     "dash==2.18.0",
#     "urllib3==1.26.16",
#     "dash-bootstrap-components",
#     "watchdog",
# ]
# ///




from dash import Dash, html, dash_table, dcc, callback, Input, Output
from plotly import graph_objs as go
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from itertools import batched, count
from glob import glob
from watchdog.observers import Observer
from watchdog.events import (
    RegexMatchingEventHandler, PatternMatchingEventHandler, 
    FileCreatedEvent, FileModifiedEvent,
    FileDeletedEvent, FileMovedEvent,
)
import time
import os
from multiprocessing import Process, Lock
import traceback
import sys
import json

toquery_loc = os.path.join(os.path.dirname(__file__), 'toquery_updated_v2.json')


def generate_graph_div(options, df, filter_fn=(lambda x:True), num_cols=4):
    rows = []
    valid_options = filter(filter_fn, options)
    for option_list in batched(valid_options, num_cols):
        cols = []
        for option in option_list:
            dff = df[df.id == option["value"]].copy()
            baseline = dff.sort_values(by=["date"]).iloc[0].followers
            def normalize_followers(followers):
                return (followers / baseline) * 100
            dff['followers'] = dff['followers'].apply(normalize_followers)
            cols.append(dbc.Col(dcc.Graph(
                id=f'graph-{option["category"]}-{option["value"]}',
                figure=px.line(dff, x='date', y='followers', title=option["label"])
            ), width=3, ))
        rows.append(dbc.Row(cols))
    return dbc.Container(rows, fluid=True)

# def generate_indicators(options, df, filter_fn):
#     valid_options = filter(filter_fn, options)
#     ndf = df.copy()
#     for name in df["name"]:
#         ndf["baseline"] = ndf[]
#     data = [
#         go.Bar(x=df['name'], y=df['value'])
#     ]

def generate_bar_graphs(id, df):
    bdf = df.groupby(["id"]).agg(min_date=('date', 'min'), max_date=('date', 'max'))
    df1 = df.merge(bdf, on=["id"])
    min_df = df1.loc[df1["min_date"] == df1["date"]][['id', 'followers','date']]
    max_df = df1.loc[df1["max_date"] == df1["date"]][['id', 'followers', 'date']]
    min_df = min_df.rename(columns={'followers':'baseline_followers'})
    max_df = max_df.rename(columns={'followers':'current_followers'})
    rdf = min_df.merge(max_df, on='id')
    rdf['change'] = (rdf['current_followers'] - rdf['baseline_followers']) / rdf['current_followers'] * 100
    rdf
    rdf.merge(df, on='id')[['id','name', 'baseline_followers', 'current_followers', 'change']]
    odf = pd.read_json(toquery_loc)
    result_df = odf.merge(rdf, on='id')
    result_df = result_df.sort_values(by=['category', 'name'], ascending=False)
    width = 0.6
    def extract_ratio(s1, s2, cond):
        def fmt(x, y):
            if cond(x, y):
                pc = 100 * (y - x) / x
                return "{:.2f}%".format(pc)
            else:
                return ""
        return s1.combine(s2, fmt)
        # percent = "%.2f" % (s1 / s2) 
        
    normed_df = result_df['current_followers'] / result_df['baseline_followers'] * 100
    data = [
        go.Bar(
            y=result_df['name'], 
            x=result_df['current_followers'], 
            text=extract_ratio(result_df['baseline_followers'], result_df['current_followers'], 
                               lambda base, curr: base <= curr),
            textposition='outside',
            name='Current', width=width, orientation='h'),
        go.Bar(
            y=result_df['name'], 
            x=result_df['baseline_followers'],
            text=extract_ratio(result_df['baseline_followers'], result_df['current_followers'],
                               lambda base, curr: base > curr), 
            textposition='outside',
            name='Baseline', width=width/2, offset=-width/4, orientation='h'),        
    ]
    maxval = max(result_df['current_followers'].max(), result_df['baseline_followers'].max()) * 1.25
    # layout = go.Layout(barmode='overlay', bargap=0.5)
    fig = go.Figure(data)
    fig.update_xaxes(range=[0, maxval])
    fig.update_layout(
        uniformtext_minsize=12,       # Minimum font size in pixels
        uniformtext_mode='show'
    )
    return dcc.Graph(
        id=id,
        figure=fig,
    )

def category_filter(category):
    def fn(df):
        return df[df.category == category].reset_index().drop(columns=['index'])
    return fn

def setup():
    # print('why twice?\n'*5)
    # try:
    #     raise Exception()
    # except Exception as e:
    #     print(traceback.print_stack())
    data_loc = os.path.join(os.path.dirname(__file__), 'data')
    id_to_query = dict()
    with open(toquery_loc) as f:
        configs = json.load(f)
        for config in configs:
            id_to_query[config['id']] = config
        print(json.dumps(configs, indent=2))
    dfs = []
    for path in glob('data/*.json'):
        data = []
        with open(path) as f:
            for line in f:
                d = json.loads(line)
                if d['id'] not in id_to_query:
                    continue
                orig = id_to_query[d['id']]
                d['name'] = orig['name']
                d['category'] = orig['category']
                data.append(d)
        df = pd.DataFrame(data)
        # df = pd.read_json(path, lines=True)
        dfs.append(df)
    df = pd.concat(dfs)
    df = df.sort_values(by=["date", "id"])
    df_dict = df[['id', 'name', 'category']].drop_duplicates().reset_index().drop(columns=['index']).to_dict()
    id_len = len(df_dict['id'])

    # Initialize the app
    app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    # all graphs
    # stuffs = (
    #     dict(value=df_dict['id'][idx], label=df_dict['name'][idx], category=df_dict['category'][idx])
    #     for idx in range(id_len)
    # )
    
    
    app.layout = [
        html.Div(children=html.H1('Socmed Metrics'), style={'textAlign': 'center'}),
        html.Div(children=[
            html.H2('Partylists'),
            generate_bar_graphs('b1', df.loc[df["category"] == "partylist"])    
        ], style={'textAlign': 'center'}),
        html.Div(children=[
            html.H2('Individuals'),
            generate_bar_graphs('b2', df.loc[df["category"] == "individual"])    
        ], style={'textAlign': 'center'}),
        html.Div(children=[
            html.H2('Mass Orgs'),
            generate_bar_graphs('b3', df.loc[df["category"] == "mass-org"])    
        ], style={'textAlign': 'center'}),
        html.Div(children=[
            html.H2('Media'),
            generate_bar_graphs('b4', df.loc[df["category"] == "media"])    
        ], style={'textAlign': 'center'}),
        html.Div(children=[
            html.H2('Artists'),
            generate_bar_graphs('b5', df.loc[df["category"] == "artist"])    
        ], style={'textAlign': 'center'}),
        html.Div(children=[
            html.H2('At Iba Pa'),
            generate_bar_graphs('b6', df.loc[df["category"] == "atbp"])    
        ], style={'textAlign': 'center'}),
        
        # html.Div(children=[
        #     fig,
        # ], style={'textAlign': 'center'}),
    ]
    # app.layout = layout

    # options = sorted(stuffs, key=lambda d: (d['category'], d['label']))
    # app.layout = [
    #     html.Div(children=html.H1('Socmed Metrics'), style={'textAlign': 'center'}),
    #     html.Div(children=[
    #         html.H2('Partylists'),
    #         generate_graph_div(options, df, (lambda opt: opt['category'] == 'partylist')),
    #     ], style={'textAlign': 'center'}),
    #     html.Div(children=[
    #         html.H2('Individuals'),
    #         generate_graph_div(options, df, (lambda opt: opt['category'] == 'individual')),
    #     ], style={'textAlign': 'center'}),
    #     html.Div(children=[
    #         html.H2('Mass Organizations'),
    #         generate_graph_div(options, df, (lambda opt: opt['category'] == 'mass-org')),
    #     ], style={'textAlign': 'center'}),
    #     html.Div(children=[
    #         html.H2('Media'),
    #         generate_graph_div(options, df, (lambda opt: opt['category'] == 'media')),
    #     ], style={'textAlign': 'center'}),
    #     html.Div(children=[
    #         html.H2('Artists'),
    #         generate_graph_div(options, df, (lambda opt: opt['category'] == 'artist')),
    #     ], style={'textAlign': 'center'}),
    # ]
    return app



class AppStarter:
    def __init__(self, patterns: list[str]):
        self._handler = PatternMatchingEventHandler(patterns=patterns)
        self._handler.on_any_event = self.on_event
        self.allowed_events = (
            FileMovedEvent, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent
        )
        self.app = None
    @property
    def handler(self):
        return self._handler
    def on_event(self, evt):
        if any(isinstance(evt, allowed_evt) for allowed_evt in self.allowed_events):
            self.restart()
    def start(self):
        if self.app is None:
            print('starting app...')
            self.app = Process(target=run_app)
            self.app.start()
        else:
            print('app already started.')
    def restart(self):
        print('stopping app...')
        # self.app.terminate()
        self.app.kill()
        start = time.time()
        while self.app.is_alive():
            print(f'still alive after {time.time() - start} seconds...')
            time.sleep(1)
        print('app is dead...')
        self.app.join()
        print('restarting app...')
        self.app = Process(target=run_app)
        self.app.start()
            

def run_app():
    # print("rerunning app...")
    # for seq in count(1):
    #     print('sleeping...', seq)
    #     time.sleep(2)
    # time.sleep(1000)
    # return setup()
    app = setup()
    app.run(debug=False, port=11111, host="0.0.0.0")
    print('is this blocking?')
    
def shutdown_app(app):
    print('shutting down')
    time.sleep(1)
    app.server.shutdown()


# Run the app
if __name__ == '__main__':
    # mylock = Lock()
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    app_starter = AppStarter(["*.json"])
    observer = Observer()
    observer.schedule(app_starter.handler, "data")
    observer.start()
    app_starter.start()
    # app.run(debug=True, port=11111, host="0.0.0.0")
    # stopper.join()
    print('kawawa\n'*10 )
    print('wut')
    while True:
        time.sleep(1)
    # observer.stop()
    # observer.join()