import pandas as pd
import plotly.graph_objs as go
import plotly.plotly as py
import statistics
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import matplotlib.pyplot as plt
import numpy as np
import radar_plot as rd
import pylab as pl
import radar_simple as rds

engine_logs = pd.read_csv('df_engine_logs.csv', header=0, sep=';')
bot_logs = pd.read_csv('df_bot_logs.csv', header=0, sep=';')

# Utils
pretty_names = {"basicNegamax": "Basic NegaMax",
                "contestNegamax": "Contest NegaMax",
                "final1": "Final 1",
                "final2": "Final 2",
                "1d": "1D Array",
                "2d": "2D Array",
                "bit": "Bit Board",
                "RANDOM": "Random Bot",
                "FINAL1": "Final 1",
                "FINAL2": "Final 2",
                "CONTEST": "Contest NegaMax",
                "BASIC": "Basic NegaMax",
                "NOTABUG": "Not A Bug"
                }

short_names = {"basicNegamax": "Bas.NM",
               "contestNegamax": "Con.NM",
               "final1": "Final1",
               "final2": "Final2",
               "1d": "1D",
               "2d": "2D",
               "bit": "BitBoard",
               "RANDOM": "Random",
               "FINAL1": "Final1",
               "FINAL2": "Final2",
               "CONTEST": "Con.NM",
               "BASIC": "Bas.NM",
               "NOTABUG": "NABug"
               }

bot_type_name_map = {
    "FINAL1": "final1",
    "FINAL2": "final2",
    "CONTEST": "contestNegamax",
    "BASIC": "basicNegamax"
}

bot_name_type_map = {
    "final1": "FINAL1",
    "final2": "FINAL2",
    "contestNegamax": "CONTEST",
    "basicNegamax": "BASIC"
}

img_layout = dict(width=1024,
                  height=800)

marker_layout = dict(
    size=3)

plot_folder = dict(
    scatter_dnt='scatter_dnt',
    depth_by_round='depth_by_round',
    scatter_dnt_html='scatter_3d_interactive',
    dnt_by_board='dnt_by_board',
    line_plot='line_plot'
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

colors_for_the_colorblind = [
    '#7F0303',  # colorblind red
    '#1F1E1E',  # colorblind dark gray
    '#2C3AFF',  # colorblind blue
    '#BFA500',  # colorblind yellow
    '#8C8882',  # colorblind light gray
]

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
    stats = dict(
        player=player1,
        opponent=player2,
        wins=0,
        draws=0,
        losses=0
    )
    df = get_engine_games_by_player(player1, player2)
    stats['wins'] = df.loc[df['winnerId'] == df['playerId']]['player1'].count()
    stats['losses'] = df.loc[(df['winnerId'] != df['playerId']) & (df['winnerId'] != 0)]['player1'].count()
    stats['draws'] = df.loc[df['winnerId'] == 0]['player1'].count()
    return stats


def print_winning_stats(player1, player2):
    stats = get_winning_stats(player1, player2)
    print(pretty_names[player1] + ' wins: ' + str(stats['wins']))
    print(pretty_names[player2] + ' wins: ' + str(stats['losses']))
    print('draws:' + str(stats['draws']))


def get_bot_types():
    return bot_logs['bot_type'].drop_duplicates().tolist()


def get_bot_names():
    df = bot_logs['player1'].drop_duplicates()
    df = df.append(bot_logs['player2'])
    return df.drop_duplicates().tolist()


def get_round_numbers():
    return bot_logs['round_number'].drop_duplicates().tolist()


def get_bot_log_by_bot_type(bot_type):
    df = bot_logs[(bot_logs['bot_type'] == bot_type)]
    df = df[(df['time'] > 0)]
    return df


def get_bot_log_by_round_number(round_number):
    return bot_logs[(bot_logs['round_number'] == round_number)]


def get_bot_log_by_round_group(group):
    return bot_logs[(bot_logs['round_number'] >= round_groups[group]['from'])
                    & (bot_logs['round_number'] <= round_groups[group]['to'])]


def get_trace_bot_attribute(bot_type, attribute):
    df = get_bot_log_by_bot_type(bot_type)
    df = df[[attribute]]
    return df[attribute].tolist()


def get_trace_bot_attribute(bot_type, attribute, player1_filter, player2_filter):
    if not (player1_filter or player2_filter):
        return get_bot_log_by_bot_type(bot_type, attribute)
    if not bot_type:
        df = bot_logs
        if player1_filter:
            df = filter_on_player1(df, player1_filter)
        if player2_filter:
            df = filter_on_player2(df, player2_filter)
        return df[attribute].tolist()
    df = get_bot_log_by_bot_type(bot_type)
    if player1_filter:
        df = filter_on_player1(df, player1_filter)
    if player2_filter:
        df = filter_on_player2(df, player2_filter)
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


def get_nps_per_bot(bot_type):
    df = get_bot_log_by_bot_type(bot_type)
    df = df['nodes'].divide(df['time'])
    df *= 1000

    return df.tolist()


def get_nps_per_bot_per_round(bot_type, round):
    df = get_bot_log_by_bot_type(bot_type)
    df = df[(df['round_number'] == round)]
    df = df['nodes'].divide(df['time'])
    df *= 1000
    df = df[df < 2500000]
    return df.tolist()


def get_nps_per_bot(bot_type, player1_filter, player2_filter):
    if not (player1_filter or player2_filter):
        return get_nps_per_bot(bot_type)
    df = get_bot_log_by_bot_type(bot_type)
    if player1_filter:
        df = filter_on_player1(df, player1_filter)
    if player2_filter:
        df = filter_on_player2(df, player2_filter)
    df = df['nodes'].divide(df['time'])
    df *= 1000
    return df.tolist()


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


def plot_nps_by_round():
    for bot in get_bot_types():
        layout = go.Layout(title='Nodes per Second per Round - ' + pretty_names[bot], width=img_layout['width'],
                           height=img_layout['height'])
        data = []
        for index in range(0, 100):
            data.append(go.Box(
                name=str(index),
                y=get_nps_per_bot_per_round(bot, index)
            ))
        plot = go.Figure(data=data, layout=layout)
        py.image.save_as(plot, filename=plot_folder['depth_by_round'] + '/nps_by_round_' + bot + '.png')


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


######### SUPER AWESOME RADAR PLOT ###########
# Ugly
def plot_radar_bots():
    spoke_labels = ['Nodes', 'Depth', 'Time', 'CacheHits', 'CacheSize']
    data = []
    labels = []

    nodes_list = get_trace_bot_attribute(None, 'nodes', None, 'RANDOM')
    depth_list = get_trace_bot_attribute(None, 'depth', None, 'RANDOM')
    time_list = get_trace_bot_attribute(None, 'time', None, 'RANDOM')
    cachesz_list = get_trace_bot_attribute(None, 'cache_size', None, 'RANDOM')
    cachedp_list = get_trace_bot_attribute(None, 'cache_hits', None, 'RANDOM')

    for bot in get_bot_types():
        labels.append(pretty_names[bot])
        stats = [
            statistics.mean(map(lambda x: (x - min(nodes_list)) / max(nodes_list),
                                get_trace_bot_attribute(bot, 'nodes', None, 'RANDOM'))),
            statistics.mean(map(lambda x: (x - min(depth_list)) / max(depth_list),
                                get_trace_bot_attribute(bot, 'depth', None, 'RANDOM'))),
            statistics.mean(map(lambda x: (x - min(time_list)) / max(time_list),
                                get_trace_bot_attribute(bot, 'time', None, 'RANDOM'))),
            statistics.mean(map(lambda x: (x - min(cachedp_list)) / max(cachedp_list),
                                get_trace_bot_attribute(bot, 'cache_hits', None, 'RANDOM'))),
            statistics.mean(map(lambda x: (x - min(cachesz_list)) / max(cachesz_list),
                                get_trace_bot_attribute(bot, 'cache_size', None, 'RANDOM'))),
        ]
        data.append(stats)

    theta = rd.radar_factory(5, frame='polygon')

    print(theta)

    fig, ax = plt.subplots(subplot_kw=dict(projection='radar'))

    colors = ['b', 'r', 'g', 'm', 'y']

    for index, row in enumerate(data):
        ax.plot(np.array(theta), np.array(row), color=colors[index])
        ax.fill(np.array(theta), np.array(row), facecolor=colors[index], alpha=0.25)
        ax.set_varlabels(spoke_labels)

    ax.legend(labels, loc=(0.9, .95),
              labelspacing=0.1, fontsize='small')

    fig.text(0.5, 0.965, 'Bot Performance vs Random (Average)',
             horizontalalignment='center', color='black', weight='bold',
             size='large')

    plt.show()


# Needs adaptation of y-axis ranges in Radar class
def plot_radar_bots2():
    fig = pl.figure(figsize=(6, 6))

    titles = ["Nodes", "Depth", "Time", "CacheHits", "CacheSize"]

    labels = [
        [0, 140000, 280000],
        [0, 5, 10],
        [0, 300, 600],
        [0, 1250, 2500],
        [0, 4250, 8500]
    ]

    colors = ['r', 'g', 'b', 'y']
    radar = rds.Radar(fig, titles, labels)
    for index, bot in enumerate(get_bot_types()):
        data = [
            statistics.mean(get_trace_bot_attribute(bot, 'nodes', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute(bot, 'depth', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute(bot, 'time', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute(bot, 'cache_hits', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute(bot, 'cache_size', None, 'RANDOM')),
        ]
        radar.plot(data, "-", lw=2, color=colors[index], alpha=0.4, label=pretty_names[bot])

    radar.ax.legend()
    pl.show()


######### LINE PLOTS ##########################
def plot_lines_bot():
    depth_color = colors_for_the_colorblind[0]
    nodes_color = colors_for_the_colorblind[1]
    nps_color = colors_for_the_colorblind[2]
    time_color = colors_for_the_colorblind[3]
    wins_color = colors_for_the_colorblind[4]
    file_name = '/line_bot_performance'
    x_axis = [pretty_names['basicNegamax'], pretty_names['contestNegamax'], pretty_names['final1'],
              pretty_names['final2']]
    trace1 = go.Scatter(
        x=x_axis,
        y=[
            statistics.mean(get_trace_bot_attribute('basicNegamax', 'depth', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute('contestNegamax', 'depth', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute('final1', 'depth', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute('final2', 'depth', None, 'RANDOM'))
        ],
        name='Depth',
        marker=dict(color=depth_color)

    )
    trace2 = go.Scatter(
        x=x_axis,
        y=[
            statistics.mean(get_trace_bot_attribute('basicNegamax', 'nodes', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute('contestNegamax', 'nodes', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute('final1', 'nodes', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute('final2', 'nodes', None, 'RANDOM'))

        ],
        name='Nodes',
        yaxis='y2',
        marker=dict(color=nodes_color)
    )
    trace3 = go.Scatter(
        x=x_axis,
        y=[
            statistics.mean(get_nps_per_bot('basicNegamax', None, 'RANDOM')),
            statistics.mean(get_nps_per_bot('contestNegamax', None, 'RANDOM')),
            statistics.mean(get_nps_per_bot('final1', None, 'RANDOM')),
            statistics.mean(get_nps_per_bot('final2', None, 'RANDOM'))
        ],
        name='Nodes Per Second',
        yaxis='y3',
        marker=dict(color=nps_color)
    )
    trace4 = go.Scatter(
        x=x_axis,
        y=[
            statistics.mean(get_trace_bot_attribute('basicNegamax', 'time', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute('contestNegamax', 'time', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute('final1', 'time', None, 'RANDOM')),
            statistics.mean(get_trace_bot_attribute('final2', 'time', None, 'RANDOM'))
        ],
        name='Time',
        yaxis='y4',
        marker=dict(color=time_color)
    )
    trace5 = go.Scatter(
        x=x_axis,
        y=[
            get_winning_stats('BASIC', 'RANDOM')['wins'],
            get_winning_stats('CONTEST', 'RANDOM')['wins'],
            get_winning_stats('FINAL1', 'RANDOM')['wins'],
            get_winning_stats('FINAL2', 'RANDOM')['wins']
        ],
        name='Wins vs Random(%)',
        marker=dict(color=wins_color)
    )
    data = [trace1, trace2, trace3, trace4]
    layout = go.Layout(
        title='Average Performance Per Bot',
        width=800,
        xaxis=dict(
            domain=[0.05, 0.95]
        ),
        yaxis=dict(
            # title='Depth',
            titlefont=dict(
                color=depth_color
            ),
            tickfont=dict(
                color=depth_color
            ),
            showgrid=False,
            nticks=5
        ),
        yaxis2=dict(
            # title='yaxis2 title',
            titlefont=dict(
                color=nodes_color
            ),
            tickfont=dict(
                color=nodes_color
            ),
            anchor='free',
            overlaying='y',
            side='left',
            # position=0.11,
            showgrid=False,
            nticks=5

        ),
        yaxis3=dict(
            # title='yaxis4 title',
            titlefont=dict(
                color=nps_color
            ),
            tickfont=dict(
                color=nps_color
            ),
            anchor='x',
            overlaying='y',
            side='right',
            showgrid=False,
            nticks=5
        ),
        yaxis4=dict(
            # title='yaxis4 title',
            titlefont=dict(
                color=time_color
            ),
            tickfont=dict(
                color=time_color
            ),
            anchor='x',
            overlaying='y',
            side='right',
            showgrid=False,
            position=0.95,
            nticks=5,
            autorange='reversed'
        )
    )
    fig = go.Figure(data=data, layout=layout)
    py.image.save_as(fig, filename=plot_folder['line_plot'] + file_name + '.png')


def plot_lines_vsNotABug():
    depth_color = colors_for_the_colorblind[1]
    nps_color = colors_for_the_colorblind[2]
    time_color = colors_for_the_colorblind[3]
    file_name = '/line_bot_notABug'
    x_axis = ['vs Random', 'vs Not A Bug']
    trace1 = go.Scatter(
        x=x_axis,
        y=[
            statistics.mean(get_trace_bot_attribute('final1', 'depth', 'FINAL1', 'RANDOM') +
                            get_trace_bot_attribute('final1', 'depth', 'FINAL1', 'RANDOM')),
            statistics.mean(get_trace_bot_attribute('final2', 'depth', 'FINAL2', 'RANDOM') +
                            get_trace_bot_attribute('final2', 'depth', 'FINAL2', 'RANDOM'))
        ],
        name='Depth',
        marker=dict(color=depth_color)

    )
    trace2 = go.Scatter(
        x=x_axis,
        y=[
            statistics.mean(get_trace_bot_attribute('final1', 'time', 'FINAL1', 'RANDOM') +
                            get_trace_bot_attribute('final1', 'time', 'FINAL1', 'RANDOM')),
            statistics.mean(get_trace_bot_attribute('final2', 'time', 'FINAL2', 'RANDOM') +
                            get_trace_bot_attribute('final2', 'time', 'FINAL2', 'RANDOM'))
        ],
        name='Time',
        yaxis='y2',
        marker=dict(color=time_color)
    )
    trace3 = go.Scatter(
        x=x_axis,
        y=[
            statistics.mean(get_nps_per_bot('final1', 'FINAL1', 'RANDOM')+
                            get_nps_per_bot('final2', 'FINAL2', 'RANDOM')),
            statistics.mean(get_nps_per_bot('final1', 'FINAL1', 'NOTABUG') +
                            get_nps_per_bot('final2', 'FINAL2', 'NOTABUG'))
        ],
        name='Nodes Per Second',
        yaxis='y3',
        marker=dict(color=nps_color)
    )
    data = [trace1, trace2, trace3]
    layout = go.Layout(
        title='Average Performance Against Random and Not A Bug',
        width=800,
        xaxis=dict(
            domain=[0.05, 0.95]
        ),
        yaxis=dict(
            # title='Depth',
            titlefont=dict(
                color=depth_color
            ),
            tickfont=dict(
                color=depth_color
            ),
            showgrid=False,
            nticks=5
        ),
        yaxis2=dict(
            # title='yaxis2 title',
            titlefont=dict(
                color=time_color
            ),
            tickfont=dict(
                color=time_color
            ),
            anchor='free',
            overlaying='y',
            side='left',
            # position=0.11,
            showgrid=False,
            nticks=5

        ),
        yaxis3=dict(
            # title='yaxis4 title',
            titlefont=dict(
                color=nps_color
            ),
            tickfont=dict(
                color=nps_color
            ),
            anchor='x',
            overlaying='y',
            side='right',
            showgrid=False,
            nticks=5
        )
    )
    fig = go.Figure(data=data, layout=layout)
    py.image.save_as(fig, filename=plot_folder['line_plot'] + file_name + '.png')


########### HORIZONTAL BAR PLOT ##########
def plot_match_results():
    matches = np.array([
        ['BASIC', 'RANDOM'],
        ['CONTEST', 'RANDOM'],
        ['FINAL1', 'RANDOM'],
        ['FINAL2', 'RANDOM'],
        ['BASIC', 'CONTEST'],
        ['CONTEST', 'FINAL1'],
        ['FINAL1', 'FINAL2'],
        ['FINAL1', 'NOTABUG'],
        ['FINAL2', 'NOTABUG']
    ])
    wins = []
    losses = []
    draws = []
    x_axis = []

    for match in reversed(matches):
        x_axis.append(
            ' vs '.join([short_names[match[0]], short_names[match[1]]])
        )
        stats = get_winning_stats(match[0], match[1])
        wins.append(
            stats['wins']
        )
        losses.append(
            stats['losses']
        )
        draws.append(
            stats['draws']
        )

    traces = []
    data = [wins, losses, draws]
    opacity = 0.6
    colors = ['rgba(2,84,0,' + str(opacity) + ')', 'rgba(138,0,2,' + str(opacity) + ')',
              'rgba(138,133,127,' + str(opacity) + ')']
    colors_lines = ['rgb(2,84,0)', 'rgb(138,0,2)', 'rgba(138,133,127,1']
    labels = ['Wins', 'Losses', 'Draws']
    for i in range(0, 3):
        traces.append(
            go.Bar(
                y=x_axis,
                x=data[i],
                name=labels[i],
                orientation='h',
                marker=dict(
                    color=colors[i],
                    line=dict(
                        color=colors_lines[i],
                        width=1
                    )
                )
            )
        )

    layout = go.Layout(
        barmode='stack',
        yaxis=dict(
        ),
        xaxis=dict(
            domain=[0.1, 1]
        )
    )

    fig = go.Figure(data=traces, layout=layout)
    py.image.save_as(fig, filename='winning_stats.png')


# plot_depth_by_round()
plot_nps_by_round()
# plot_bot_dnt_scatter(True)
# plot_round_dnt_scatter(True)
# plot_round_group_dnt_scatter(True)
# plot_boards_dnt_bars()
# plot_bots_dnt_bars()

# plot_radar_bots2()
bot = 'final1'
print(
    [
        statistics.mean(get_trace_bot_attribute(bot, 'nodes', None, 'RANDOM')),
        statistics.mean(get_trace_bot_attribute(bot, 'depth', None, 'RANDOM')),
        statistics.mean(get_trace_bot_attribute(bot, 'time', None, 'RANDOM')),
        statistics.mean(get_trace_bot_attribute(bot, 'cache_hits', None, 'RANDOM')),
        statistics.mean(get_trace_bot_attribute(bot, 'cache_size', None, 'RANDOM'))
    ])

