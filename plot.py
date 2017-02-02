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


def get_bot_log_by_bot_type(bot_type):
    return bot_logs[(bot_logs['bot_type'] == bot_type)]


def get_depth_traces_by_game(bot_type, game_number):
    df = get_bot_log_by_bot_type(bot_type)
    df = df[(df['game_number'] == game_number)][['depth']]
    return df['depth'].tolist()


def get_depth_traces_by_round(bot_type, round_number):
    df = get_bot_log_by_bot_type(bot_type)
    df = df[(df['round_number'] == round_number)][['depth']]
    return df['depth'].tolist()


# Plotting
for bot in get_bot_types():
    layout = go.Layout(title='Depth per Round - ' + pretty_names[bot], width=1024, height=800)
    data = []
    for index in range(0, 100):
        data.append(go.Box(
            name=str(index),
            y=get_depth_traces_by_round(bot, index)
        ))
    plot = go.Figure(data=data, layout=layout)
    py.image.save_as(plot, filename='depth_by_round/depth_by_round_' + bot + '.png')






# print(get_winning_stats('CONTEST', 'FINAL1'))
# print(get_winning_stats('BASIC', 'CONTEST'))

# print(get_bot_log_by_bot_type('final1')['player1'].count())
# print(get_bot_log_by_bot_type('final1').groupby(['player1','player2'])['bot_type'].count())
