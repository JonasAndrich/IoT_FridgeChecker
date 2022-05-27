#! /home/ubuntu/fridgechecker/bin/python
# -*- coding: utf-8 -*-

from dash import dash_table, html, Dash, dcc
import sqlite3
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, date, timedelta
import numpy as np

PATH = "/home/ubuntu/fridgechecker/Database.db"



# Access to database and create a pandas dataframe from data
# Die Table/Relation heißt "BUTTON_data", darin sind die Attribute "timestamp" und "state" enthalten.
def gethistdata():
    # switch dependent of db source
    conn = sqlite3.connect(PATH, check_same_thread=False)
    # conn = sqlite3.connect('../sensorsData.db', check_same_thread=False)
    query = "SELECT * FROM BUTTON_data WHERE timestamp NOT BETWEEN '2020-07-04' AND '2020-07-19' ORDER BY timestamp"
    df = pd.read_sql_query(query, conn)
    conn.close()

    # converts timestamp to datetime and adds offset time, because date was stored in db as utc
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(str))

    # timstamp wird Dataframe-Index
    df = df.set_index('timestamp')
    # print(df.index)
    # https://stackoverflow.com/questions/16777570/calculate-time-difference-between-pandas-dataframe-indices

    # This creates the Duration between Openings
    df["ser_diff [s]"] = df.index.to_series().diff().shift(-1).fillna(pd.Timedelta(seconds=0))
    print(df.head(10))
    return df


def mean_access_today(df):
    # Der Zeitpunkt "today" und "yesterday" wird aus dem Datetimeobjekt now abgleitet.

    # calculates time object now
    now = datetime.now()

    # calculates a string
    today = now.strftime("%Y-%m-%d")

    try:
        # Die Summe der Öffnungen (state = 1) heute
        opens_today = df.loc[today]["state"].sum()
        print(opens_today)

        # im nächsten Schritt kann ich die Öffnungszeiten für einen Tag (yesterday or today)
        # oder die gesamte Periode zusammenzählen.
        # Nur die Einträge von Heute und diejenigen in denen state = 1, also "open" sind.
        # super eleganter Befehl
        sum_open_today = df["ser_diff [s]"][df["state"] == 1].loc[today].sum()
        print(sum_open_today)

        # Mean open Time today minutes
        mean_open_time_today = sum_open_today / opens_today

        print(mean_open_time_today)
        # print(type(mean_open_time_today))
        return ["Heute", int(opens_today), int(sum_open_today.total_seconds()),
                int(mean_open_time_today / np.timedelta64(1, 's'))]
    except KeyError:
        print("Der Kühlschrank wurde heute nicht geöffnet!")
        return ["Heute", 0, 0, 0]


def mean_access_yesterday(df):
    # define yesterday in datetime to be able to use loc method
    yesterday = date.today() - timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")

    try:
        # Number of openings (state = 1) yesterday
        opens_yesterday = df.loc[yesterday]["state"].sum()
        print(opens_yesterday)

        # Sum opening time yesterday
        sum_open_yesterday = df["ser_diff [s]"][df["state"] == 1].loc[yesterday].sum()
        print(sum_open_yesterday)

        # Mean opening time yesterday in minutes
        mean_open_time_yesterday = sum_open_yesterday / opens_yesterday

        print(mean_open_time_yesterday)

        return ["Gestern", int(opens_yesterday), int(sum_open_yesterday.total_seconds()),
                int(mean_open_time_yesterday / np.timedelta64(1, 's'))]
    except KeyError:
        print("Der Kühlschrank wurde gestern nicht geöffnet!")
        return ["Gestern", 0, 0, 0]


def mean_access(df):
    # Time delta from first and last index item, which is a time object
    all_days = df.index[-1] - df.index[0]
    all_days = all_days.days

    # convert daytime object to int
    if all_days == 0:
        all_days = 1

    # Sum of all openings
    all_open = df["state"].sum()

    # Total opening time
    time_toal_accumulate = df["ser_diff [s]"][df["state"] == 1].sum()

    print(all_days)

    # Mean-opening time per day

    mean_open_time = time_toal_accumulate / all_days
    # print(time_toal_accumulate)

    print("mean_open_time", mean_open_time.total_seconds())

    # Mean openings per day
    mean_open_per_days = all_open / all_days
    print("Mean openings per day", mean_open_per_days)

    # Mean opening time
    mean_open_time_all_time = mean_open_time / mean_open_per_days
    print("Mean opening time", mean_open_time_all_time)

    # np.diff(mean_open_time_all_time)/np.timedelta64(1, 's')

    return ["Vergangenheit", int(mean_open_per_days), int(mean_open_time.total_seconds()),
            int(mean_open_time_all_time / np.timedelta64(1, 's'))]


def data_assembly():
    df = gethistdata()

    l1 = mean_access_today(df)
    l2 = mean_access_yesterday(df)
    l3 = mean_access(df)

    l4 = [l1, l2, l3]
    print(l4)
    df_assembled = pd.DataFrame(l4, columns=["Time", "Anzahl Öffnungen pro Tag", "Summe Dauer Öffnungen pro Tag [s]",
                                             "Mittlere Dauer pro Öffnung [s]"])
    return df_assembled, df


app = Dash(__name__)


# Allows to update data if page is reloaded
# Option 1 - Make app.layout a function (https://dash.plot.ly/live-updates 293) and set the data on page load
# and pass it through to different callbacks with hidden divs: https://dash.plot.ly/sharing-data-between-callbacks 138

def serve_layout():
    df_assembled, df = data_assembly()

    # https://chrisalbon.com/python/data_wrangling/group_pandas_data_by_hour_of_the_day/
    grouped = (df["state"].groupby(df.index.hour).count())
    # test = grouped.aggregate(np.sum)
    print(grouped.index)
    print(grouped)

    layout = html.Div(children=[
        html.H1(children='Fridge-Checker'),
        # html.Div(children='''Dash: A web application framework for Python.'''),
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df_assembled.columns],
            data=df_assembled.to_dict('records')
        )
        ,
        dcc.Graph(
            id='Opening Events over Time',
            figure={
                'data': [
                    go.Scatter(
                        x=df[df["state"] == 1].index,
                        y=df[df["state"] == 1]["ser_diff [s]"].dt.seconds,
                        mode='markers',
                        opacity=0.7,
                        marker={
                            'size': 10,
                            'line': {'width': 0.5, 'color': 'white'}
                        }

                    )
                ]

                , 'layout': go.Layout(
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Opening Time [s]'},
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    # legend={'x': 0, 'y': 1},
                    hovermode='closest'
                )

            }
        ),
        dcc.Graph(
            id='Histogram',
            figure={
                'data': [
                    # HIER TODO->Y Wert vorher Groupby series zum Dataframe machen und dann  wie oben.
                    {'x': grouped.index, 'y': grouped, 'type': 'bar'}

                ],
                'layout': {
                    'title': 'Histogram der Öffnungen nach Tageszeit'
                }
            }
        )

    ])

    return layout


app.layout = serve_layout

if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run_server(port=8080, host='0.0.0.0')
