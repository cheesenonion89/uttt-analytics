import pandas as pd
import os
import re

player = {"I": "BASIC",
          "II": "CONTEST",
          "III": "FINAL1",
          "IV": "FINAL2",
          "R": "RANDOM",
          "BUG": "NOTABUG"}

log_path = 'C:\\Users\\Markus\\IdeaProjects\\uttt-engine\\simulation_out'

bot_logs_col = ['player1', 'player2', 'bot_type', 'game_number', 'nodes', 'depth', 'move', 'cache_hits', 'time',
                'cache_size', 'move_number', 'round_number']

engine_logs_col = ['player1', 'player2', 'game_number', 'playerId', 'winnerId', 'wonMacroFieldsP1', 'wonMacroFieldsP2',
                   'macroBoard', 'mBoard']

bot_logs = pd.DataFrame(columns=bot_logs_col)

engine_logs = pd.DataFrame(columns=engine_logs_col)


def get_player_prefix(file_path):
    match = re.search('[A-Z]{1,3}_[A-Z]{1,3}_[a-z]*', file_path)
    if match:
        groups = match.group(0).split('_')
        return [player[groups[0]], player[groups[1]], groups[2]]
    else:
        return None


# Iterate over all folders in simulation_out
for root, dir, files in os.walk(log_path):
    # Derive the log type and playing bots from the folder name e.g. FINAL1 FINAL2 enginelog
    file_info = get_player_prefix(root)

    # Get player names and type of log from the file info
    if file_info:
        player1 = file_info[0]
        player2 = file_info[1]
        log_type = file_info[2]

    # declare game counters
    bot_log_gamecounter = 0
    engine_log_gamecouter = 0

    # remember first bot to resest bot game counter
    first_bot_type = ''

    for file in files:
        # For bot logs, increment game counter per file (reset game counter after first bot)
        if log_type == 'logs':
            bot_type = file.split('_')[0]

            if bot_type != first_bot_type:
                bot_log_gamecounter = 0
                first_bot_type = bot_type

            bot_log_gamecounter += 1
            # Build the metadata to append before each line
            meta_data = pd.DataFrame(data=[(player1, player2, bot_type, bot_log_gamecounter)])

            # Read each line, append metadata before and write result to data frame
            for df in pd.read_csv(root + "\\" + file, sep=';', header=None, skiprows=[0], chunksize=1):
                row = pd.concat([meta_data, df], axis=1)
                row.columns = bot_logs_col
                bot_logs = bot_logs.append(row, ignore_index=True)

        # For engine output increment game counter per row in csv
        if log_type == 'enginelogs':

            # Read each line, append metadata before and write result to data frame
            for df in pd.read_csv(root + "\\" + file, sep=';', header=None, skiprows=[0], chunksize=1):
                engine_log_gamecouter += 1
                meta_data = pd.DataFrame(data=[(player1, player2, engine_log_gamecouter)])
                row = pd.concat([meta_data, df], axis=1)
                row.columns = engine_logs_col
                engine_logs = engine_logs.append(row, ignore_index=True)

# Write the final data frames to csv for faster reloading
bot_logs.to_csv('df_bot_logs_index.csv', sep=';')
engine_logs.to_csv('df_engine_logs_index.csv', sep=';')


###
# final1 = 0
# final2 = 0
# contestNegamax = 0
# basicNegamax = 0
# print(bot_logs[['player1', 'player2','bot_type','game_number']].drop_duplicates())
# print(engine_logs[['player1','player2','game_number']].drop_duplicates())
# if bot_type == 'contestNegamax':
#    contestNegamax += 1
# if bot_type == 'basicNegamax':
#    basicNegamax += 1
# if bot_type == 'final1':
#    final1 += 1
# if bot_type == 'final2':
#    final2 += 1
#    # print(bot_type)
#    # print(first_bot_type)
