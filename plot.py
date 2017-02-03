import pandas as pd
import plotly.graph_objs as go
import plotly.plotly as py
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

engine_logs = pd.read_csv('df_engine_logs.csv', header=0, sep=';')
bot_logs = pd.read_csv('df_bot_logs.csv', header=0, sep=';')

# Utils
pretty_names = {"basicNegamax": "Basic NegaMax",
                "contestNegamax": "Contest NegaMax",
                "final1": "Final 1",
                "final2": "Final 2"
                }

img_layout = dict(width=1024,
                  height=800)

marker_layout = dict(
    size=3)

plot_folder = dict(
    scatter_dnt='scatter_dnt',
    depth_by_round='depth_by_round',
    scatter_dnt_html='scatter_3d_interactive'
)


def get_player_combinations(df):
    return df[['player1', 'player2']].drop_duplicates()


# Functions on engine_logs
def get_engine_games_by_player(player1, player2):
    return engine_logs.loc[(engine_logs['player1'] == player1) & (engine_logs['player2'] == player2)]


def get_winning_stats(player1, player2):
    df = get_engine_games_by_player(player1, player2)
    result = ""
    result += str(player1) + " : " + str(df.loc[df['winnerId'] == df['playerId']]['player1'].count()) + "\n"
    result += str(player2) + " : " + str(
        df.loc[(df['winnerId'] != df['playerId']) & (df['winnerId'] != 0)]['player1'].count()) + "\n"
    result += "draw" + " : " + str(df.loc[df['winnerId'] == 0]['player1'].count())
    return result


# Functions on bot_logs
def get_bot_types():
    return bot_logs['bot_type'].drop_duplicates().tolist()


def get_round_numbers():
    return bot_logs['round_number'].drop_duplicates().tolist()


def get_bot_log_by_bot_type(bot_type):
    return bot_logs[(bot_logs['bot_type'] == bot_type)]


def get_bot_log_by_round_number(round_number):
    return bot_logs[(bot_logs['round_number'] == round_number)]


def get_trace_bot_attribute(bot_type, attribute):
    df = get_bot_log_by_bot_type(bot_type)
    df = df[[attribute]]
    return df[attribute].tolist()


def get_trace_round_attribute(round_number, attribute):
    df = get_bot_log_by_round_number(round_number)
    df = df[[attribute]]
    return df[attribute].tolist()


def get_traces_bot_round(bot_type, round_number):
    df = get_bot_log_by_bot_type(bot_type)
    df = df[(df['round_number'] == round_number)][['depth']]
    return df['depth'].tolist()


def get_dnt_per_bot(bot_type):
    df = get_bot_log_by_bot_type(bot_type)
    return df[['depth', 'nodes', 'time']]


def get_dnt_per_round(round_number):
    df = get_bot_log_by_round_number(round_number)
    return df[['depth', 'nodes', 'time']]


# Plotting Functions
def plot_depth_by_round():
    for bot in get_bot_types():
        layout = go.Layout(title='Depth per Round - ' + pretty_names[bot], width=img_layout['width'],
                           height=img_layout['height'])
        data = []
        for index in range(0, 100):
            data.append(go.Box(
                name=str(index),
                y=get_traces_bot_round(bot, index)
            ))
        plot = go.Figure(data=data, layout=layout)
        py.image.save_as(plot, filename=plot_folder['depth_by_round'] + '/depth_by_round_' + bot + '.png')


def plot_bot_dnt_scatter(viz):
    data = []
    for bot in get_bot_types():
        trace = go.Scatter3d(
            name=pretty_names[bot],
            x=get_trace_bot_attribute(bot, 'depth'),
            y=get_trace_bot_attribute(bot, 'nodes'),
            z=get_trace_bot_attribute(bot, 'time'),
            mode='markers',
            marker=dict(
                size=marker_layout['size']
            )
        )
        data.append(trace)
    layout = go.Layout(
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
        ),
        scene=dict(
            xaxis=dict(
                title="Depth"
            ),
            yaxis=dict(
                title="Nodes"
            ),
            zaxis=dict(
                title="Time"
            )
        )
    )
    fig = go.Figure(data=data, layout=layout)
    py.image.save_as(fig, filename=plot_folder['scatter_dnt'] + '/scatter_test.png')
    if viz:
        plot(fig, filename=plot_folder['scatter_dnt_html']+'/scatter_dnt_by_bot.html')


def plot_round_dnt_scatter(viz):
    data = []
    for round_number in get_round_numbers():
        trace = go.Scatter3d(
            name=str(round_number),
            x=get_trace_round_attribute(round_number, 'depth'),
            y=get_trace_round_attribute(round_number, 'nodes'),
            z=get_trace_round_attribute(round_number, 'time'),
            mode='markers',
            marker=dict(
                size=marker_layout['size']
            )
        )
        data.append(trace)
    layout = go.Layout(
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
        ),
        scene=dict(
            xaxis=dict(
                title="Depth"
            ),
            yaxis=dict(
                title="Nodes"
            ),
            zaxis=dict(
                title="Time"
            )
        )
    )
    fig = go.Figure(data=data, layout=layout)
    py.image.save_as(fig, filename=plot_folder['scatter_dnt'] + '/scatter_dnt_by_round.png')
    if viz:
        plot(fig, filename=plot_folder['scatter_dnt_html']+'/scatter_dnt_by_round.html')


# plot_depth_by_round()
# plot_bot_dnt_scatter(True)
plot_round_dnt_scatter(True)

