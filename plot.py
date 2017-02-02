import pandas as pd

engine_logs = pd.read_csv('df_engine_logs.csv', header=0, sep=';')
bot_logs = pd.read_csv('df_bot_logs.csv', header=0, sep=';')


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


def get_player_combinations(df):
    return df[['player1', 'player2']].drop_duplicates()


print(get_winning_stats('CONTEST', 'FINAL1'))
print(get_winning_stats('BASIC', 'CONTEST'))
