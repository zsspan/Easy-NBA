"""
Module contains machine learning functions to determine
similarity. Hosts a KNN model to find closest players.
"""

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import pandas as pd

from .database.db_operations import get_player_info, get_player_name, query_all_master_table, query_all_players

FEATS = ['G', 'PTS', 'TRB', 'AST', 'STL', 'BLK', 'FG%', '3P%', 'FG%','FT%', 'TOV']

# deprecated for now
def create_master_table():
    players = query_all_players()
    
    player_data = []
    
    pos_mapping = {
        'PG': 1,
        'SG': 2,
        'SF': 3,
        'PF': 4,
        'C': 5
    }
    
    for p in players:
        career_row = next((row for row in p.reg_stats if row.season == 'Career'), None)
        
        if career_row:
            info = get_player_info(p.name)
            pos = info.get('position')[0]
            
            pos_num = pos_mapping.get(pos)  # convert position to a numeric value

            career_dict = {
                'Player_ID': p.id,
                'Pos': pos_num, 
                'G': career_row.games,
                'PTS': career_row.points,
                'TRB': career_row.rebounds,
                'AST': career_row.assists,
                'STL': career_row.steals,
                'BLK': career_row.blocks,
                'FG%': career_row.fg_percentage,
                '3P%': career_row.three_point_percentage,
                'FT%': career_row.ft_percentage,
                'TOV':career_row.turnovers
            }
            
            player_data.append(career_dict)
    
    df = pd.DataFrame(player_data)
    return df

# slightly more optimized
def create_master_table2():
    master_players = query_all_master_table()
    columns = [
        'Player_ID', 'G', 'Pos', 'PTS', 'TRB', 'AST',
        'STL', 'BLK', 'TOV', 'FG%', '3P%',
        'FT%'
    ]
    
    data = []

    for player in master_players:
        data.append([
            player.player_id,
            player.games,
            player.pos,
            player.points,
            player.rebounds,
            player.assists,
            player.steals,
            player.blocks,
            player.turnovers,
            player.fg_percentage,
            player.three_point_percentage,
            player.free_throw_percentage,
        ])
    
    df = pd.DataFrame(data, columns=columns)
    return df

def scale_data(df):
    # adjust weights
    df['Pos'] = df['Pos'] * 2
    df['G'] = df['G'] * 0.5

    df['FG%'] = df['FG%'] * 0.75
    df['3P%'] = df['3P%'] * 0.75
    df['FT%'] = df['FT%'] * 0.25

    df['TOV'] = df['TOV'] * 0.5


    scaler = StandardScaler()
    df[FEATS] = scaler.fit_transform(df[FEATS])  # apply scaling
    
    return df


def closest_player_KNN(scaled_df, player_id):
    """Use KNN to find the most similar player"""
    # extract player data (excluding the 'Player_ID' and 'Pos')
    KNN_N = 5
    NUM_PLAYERS = 1

    features = scaled_df[FEATS]

    knn = NearestNeighbors(n_neighbors=KNN_N, metric='euclidean')
    knn.fit(features)

    player_row = scaled_df[scaled_df['Player_ID'] == player_id]
    player_vector = player_row[FEATS]

    distances, indices = knn.kneighbors(player_vector)

    # get the closest player's data
    closest_player_index = indices[0][1:NUM_PLAYERS + 1]
    closest_player = scaled_df.iloc[closest_player_index]['Player_ID']

    return closest_player

def get_closest_player(id: int) -> str:
    """Returns the closest player name to player with given id."""
    try:
        scaled = scale_data(create_master_table2())
        # scaled = scale_data(create_master_table())
        
        closest_ids = closest_player_KNN(scaled, id)
        closest_names = [get_player_name(player_id) for player_id in closest_ids]
        
        create_master_table2()
        return closest_names
    
    # sometimes KNN function returns value error, fix later
    except ValueError as e:
        print(f"ValueError: {e}")
        return "Oops! The system couldn't find a player due to a value error"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Oops! An unexpected issue occurred"
