import pandas as pd
import plotly.graph_objs as go
import plotly.plotly as py
import statistics
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

engine_logs = pd.read_csv('df_engine_logs.csv', header=0, sep=';')
bot_logs = pd.read_csv('df_bot_logs.csv', header=0, sep=';')

# Utils
pretty_names = {"basicNegamax": "Basic NegaMax",
                "contestNegamax": "Contest NegaMax",
                "final1": "Final 1",
                "final2": "Final 2",
                "1d": "1D Array",
                "2d": "2D Array",
                "bit": "Bit Board"
                }

img_layout = dict(width=1024,
                  height=800)

marker_layout = dict(
    size=3)

plot_folder = dict(
    scatter_dnt='scatter_dnt',
    depth_by_round='depth_by_round',
    scatter_dnt_html='scatter_3d_interactive',
    dnt_by_board='dnt_by_board'
)

round_groups = [
    {'from': 1, 'to': 5},
    {'from': 6, 'to': 10},
    {'from': 11, 'to': 15},
    {'from': 16, 'to': 20},
    {'from': 21, 'to': 25},
    {'from': 26, 'to': 40}
]

bot_board_map = dict(
    basicNegamax='2d Array',
    contestNegamax='1d Array',
    final1='Bit Board',
    final2='Bit Board'
)

board_bot_map = {
    '2d': 'basicNegamax',
    '1d': 'contestNegamax',
    'bit': ['final1', 'final2']
}

board_types = ['2d', '1d', 'bit']


def get_player_combinations(df):
    return df[['player1', 'player2']].drop_duplicates()


def filter_on_player1(df, player):
    return df[(df['player1'] == player)]


def filter_on_player2(df, player):
    return df[(df['player2'] == player)]


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


def get_bot_log_by_round_group(group):
    return bot_logs[(bot_logs['round_number'] >= round_groups[group]['from'])
                    & (bot_logs['round_number'] <= round_groups[group]['to'])]


def get_trace_bot_attribute(bot_type, attribute):
    df = get_bot_log_by_bot_type(bot_type)
    df = df[[attribute]]
    return df[attribute].tolist()


def get_trace_round_attribute(round_number, attribute):
    df = get_bot_log_by_round_number(round_number)
    df = df[[attribute]]
    return df[attribute].tolist()


def get_trace_roundgroup_attribute(group, attribute):
    df = get_bot_log_by_round_group(group)
    df = df[[attribute]]
    return df[attribute].tolist()


def get_trace_board_attribute(board, attribute):
    bot = board_bot_map[board]
    if isinstance(bot, list):
        result = pd.DataFrame(columns=bot_logs.columns)
        for b in bot:
            result = result.append(get_bot_log_by_bot_type(b))
        return result[attribute].tolist()
    else:
        df = get_bot_log_by_bot_type(bot)
        return df[attribute].tolist()


def get_trace_board_attribute(board, attribute, player1_filter, player2_filter):
    if not (player1_filter or player2_filter):
        return get_trace_board_attribute(board, attribute)
    else:
        bot = board_bot_map[board]
        if isinstance(bot, list):
            print("ISALIST")
            result = pd.DataFrame(columns=bot_logs.columns)
            for b in bot:
                df = get_bot_log_by_bot_type(b)
                if player1_filter:
                    df = filter_on_player1(df, player1_filter)
                if player2_filter:
                    df = filter_on_player2(df, player2_filter)
                result = result.append(df)
            return result[attribute].tolist()
        else:
            df = get_bot_log_by_bot_type(bot)
            if player1_filter:
                df = filter_on_player1(df, player1_filter)
            if player2_filter:
                df = filter_on_player2(df, player2_filter)
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


######################################################################################################################
##################################################### PLOTTING  ######################################################

######## BOX PLOTS ########
# Depth per round over all games
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


######## BAR PLOTS ########
def plot_boards_dnt_bars():
    file_name = 'dnt_by_board_gg_random'
    player1_filter = None
    player2_filter = 'RANDOM'
    data = []

    for index, board in enumerate(board_types):
        trace = go.Bar(
            x=['Depth', 'Nodes', 'Time'],
            y=[
                statistics.mean(get_trace_board_attribute(board, 'depth', player1_filter, player2_filter)),
                statistics.mean(get_trace_board_attribute(board, 'nodes', player1_filter, player2_filter)),
                statistics.mean(get_trace_board_attribute(board, 'time', player1_filter, player2_filter))
            ],
            name=pretty_names[board]
            # yaxis='y'+str(index+1)
        )
        data.append(trace)

    layout = go.Layout(
        barmode='group',
        title='Double Y Axis Example',
        # xaxis=dict(
        #    domain=[0.3, 1]
        # ),
        # yaxis=dict(
        #    title='Depth',
        #    overlaying='y'
        # ),
        # yaxis2=dict(
        #    title='Nodes',
        #    titlefont=dict(
        #        color='rgb(148, 103, 189)'
        #    ),
        #    tickfont=dict(
        #        color='rgb(148, 103, 189)'
        #    ),
        #    overlaying='y',
        #    position=0.1,
        #    side='left'
        # ),
        # yaxis3=dict(
        #    title='Time',
        #    overlaying='y',
        #    position=0.2,
        #    side='left'
        # )
    )

    fig = go.Figure(data=data, layout=layout)

    py.image.save_as(fig, filename=plot_folder['dnt_by_board'] + file_name + '.png')


def plot_bots_dnt_bars():
    dimensions = ['depth', 'nodes', 'time']
    file_name = 'dnt_by_board2_gg_random'
    player1_filter = None
    player2_filter = 'RANDOM'
    data = []

    for index, dimension in enumerate(dimensions):

        trace = go.Bar(
            x=['2D Array', '1D Array', 'BitBoard'],
            y=[
                statistics.mean(get_trace_board_attribute('2d', dimension, player1_filter, player2_filter)),
                statistics.mean(get_trace_board_attribute('1d', dimension, player1_filter, player2_filter)),
                statistics.mean(get_trace_board_attribute('bit', dimension, player1_filter, player2_filter))
            ],
            opacity=0.5,
            name=dimension,
            yaxis='y' + str(index + 1)
        )
        data.append(trace)

    layout = go.Layout(
        barmode='group',
        title='Mean Depth, Nodes and Time per Board',
        xaxis=dict(
            domain=[0.3, 1]
        ),
        yaxis=dict(
            title='Depth',
            overlaying='y'
        ),
        yaxis2=dict(
            title='Nodes',
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            overlaying='y',
            position=0.1,
            side='left'
        ),
        yaxis3=dict(
            title='Time',
            overlaying='y',
            position=0.2,
            side='left'
        )
    )

    fig = go.Figure(data=data, layout=layout)

    py.image.save_as(fig, filename=plot_folder['dnt_by_board'] + file_name + '.png')


######## 3D SCATTER ########
#  3d Scatter over Depth, Nodes, Time, colorized by Bot
def plot_bot_dnt_scatter(viz):
    file_name = '/scatter_dnt_by_bot'
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
        title='Detpth, Nodes, Time by Bot',
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
    py.image.save_as(fig, filename=plot_folder['scatter_dnt'] + file_name + '.png')
    if viz:
        plot(fig, filename=plot_folder['scatter_dnt_html'] + file_name + '.html')


# 3d Scatter over Depth, Nodes, Time, colorized by Round
def plot_round_dnt_scatter(viz):
    file_name = '/scatter_dnt_by_round'
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
        title='Depth, Nodes, Time by Round',
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
    py.image.save_as(fig, filename=plot_folder['scatter_dnt'] + file_name + '.png')
    if viz:
        plot(fig, filename=plot_folder['scatter_dnt_html'] + file_name + '.html')


# 3d Scatter over Depth, Nodes, Time, colorized by Round Groups
def plot_round_group_dnt_scatter(viz):
    file_name = '/scatter_dnt_by_round_group'
    data = []
    for i in range(0, len(round_groups) - 1):
        trace = go.Scatter3d(
            name=str(round_groups[i]['from']) + '-' + str(round_groups[i]['to']),
            x=get_trace_roundgroup_attribute(i, 'depth'),
            y=get_trace_roundgroup_attribute(i, 'nodes'),
            z=get_trace_roundgroup_attribute(i, 'time'),
            mode='markers',
            marker=dict(
                size=marker_layout['size']
            )
        )
        data.append(trace)
    layout = go.Layout(
        title='Detpth, Nodes, Time by Round Group',
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
    py.image.save_as(fig, filename=plot_folder['scatter_dnt'] + file_name + '.png')
    if viz:
        plot(fig, filename=plot_folder['scatter_dnt_html'] + file_name + '.html')


# plot_depth_by_round()
# plot_bot_dnt_scatter(True)
# plot_round_dnt_scatter(True)
# plot_round_group_dnt_scatter(True)
# plot_boards_dnt_bars()
plot_bots_dnt_bars()
