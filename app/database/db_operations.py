"""
Module that contains all necessary database operations. Includes
functions for reading, writing, updating, and reformatting queried
data.
"""

from .data_retrieval import PlayerInfo
from ..models.TableModels import MasterPlayer, db, Player, RegularSeason, PostSeason, PlayerInfo
import pandas as pd

def add_player(player_query, reg, playoffs, info: dict):
    "Writes a new player to the DB"
    try:
        new_player = Player(name=player_query)
        db.session.add(new_player)
        db.session.commit()

        add_regular_season_stats(new_player.id, reg)
        add_post_season_stats(new_player.id, playoffs)
        add_player_info(new_player.id, info)

        db.session.commit()
    
    except Exception as e:
        print("Error adding player:", e)
        db.session.rollback()
        return None

def add_regular_season_stats(player_id: int, reg) -> None:
    """Adds regular season stats for the player."""
    for index in range(len(reg)):
        reg_season_entry = RegularSeason(
            player_id=player_id,
            season=reg.iloc[index]['Season'],
            team=reg.iloc[index]['Team'],
            pos=reg.iloc[index]['Pos'],
            games=int(reg.iloc[index]['G']),
            points=reg.iloc[index]['PTS'],
            rebounds=reg.iloc[index]['TRB'],
            assists=reg.iloc[index]['AST'],
            steals=reg.iloc[index]['STL'],
            blocks=reg.iloc[index]['BLK'],
            fg_percentage=(reg.iloc[index]['FG%']),  # Parse percentage
            three_point_percentage=(reg.iloc[index]['3P%']),
            ft_percentage=(reg.iloc[index]['FT%']),
            turnovers=reg.iloc[index]['TOV'],
            minutes=(reg.iloc[index]['MP'])
        )
        db.session.add(reg_season_entry)


def add_post_season_stats(player_id: int, playoffs) -> None:
    """Adds post season stats for the player."""
    for index in range(len(playoffs)):
        post_season_entry = PostSeason(
            player_id=player_id,
            season=playoffs.iloc[index]['Season'],
            team=playoffs.iloc[index]['Team'],
            pos=playoffs.iloc[index]['Pos'],
            games=int(playoffs.iloc[index]['G']),
            points=playoffs.iloc[index]['PTS'],
            rebounds=playoffs.iloc[index]['TRB'],
            assists=playoffs.iloc[index]['AST'],
            steals=playoffs.iloc[index]['STL'],
            blocks=playoffs.iloc[index]['BLK'],
            fg_percentage=(playoffs.iloc[index]['FG%']),  # Parse percentage
            three_point_percentage=(playoffs.iloc[index]['3P%']),
            ft_percentage=(playoffs.iloc[index]['FT%']),
            turnovers=playoffs.iloc[index]['TOV'],
            minutes=(playoffs.iloc[index]['MP'])

        )
        db.session.add(post_season_entry)


def add_player_info(player_id: int, info: dict) -> None:
    """Adds player info to the database."""
    name = info.get('player_name')
    link = info.get('img_link')
    positions = info.get('position', [])
    teams = info.get('teams', [])
    awards = info.get('awards', [])

    # join lists into strings
    positions_str = ', '.join(positions) if positions else None
    teams_str = ', '.join(teams) if teams else None
    awards_str = ', '.join(awards) if awards else None

    player_info = PlayerInfo(
        player_id=player_id,
        link=link,
        positions=positions_str,
        teams=teams_str,
        awards=awards_str,
        case_name=name
    )

    db.session.add(player_info)

def get_player_object(player_query: str):
    """Given a player name, fxn queries for player in the DB""" 
    try:
        player = Player.query.filter_by(name=player_query).first()
        if player:
            return player
        return None
    
    except Exception as e:
        print("Error retrieving player data:", e)
        return None

def get_player_tables(player_sql):
    """Given a player name, fxn queries for it in the DB"""
    if player_sql is None:
        return None, None
    
    reg_query = RegularSeason.query.filter_by(player_id=player_sql.id).all()
    playoffs_query = PostSeason.query.filter_by(player_id=player_sql.id).all()
            
    return reg_query, playoffs_query

def get_player_name(id: int) -> str:
    name = PlayerInfo.query.filter_by(player_id=id).first().case_name
    return name

def adjust_read_df_index(df: pd.DataFrame):
    if df is None or df.empty:
        return df
    career_index = df[df['Season'] == 'Career'].index[0]
    new_index = list(range(career_index))  # Original indices before "Career"

    for i in range(career_index, len(df)):
        new_index.append(f'TOT_{i - career_index + 1}')

    df.index = new_index
    return df

def convert_reg_to_df(reg_query):
    """Converts regular season SQL table to viewable pandas DataFrame"""
    try:
        reg_data = [{
            'ID': season.id,
            'Season': season.season,
            'Team': season.team,
            'Pos': season.pos,
            'G': season.games,
            'PTS': season.points,
            'TRB': season.rebounds,
            'AST': season.assists,
            'STL': season.steals,
            'BLK': season.blocks,
            'FG%': season.fg_percentage,
            'FT%': season.ft_percentage,
            '3P%': season.three_point_percentage,
            'TOV': season.turnovers,
            'MP': season.minutes
        } for season in reg_query]

        reg_df = pd.DataFrame(reg_data)

        # sort the DataFrame by ID and reset index
        reg_df.sort_values(by='ID', inplace=True)
        reg_df.reset_index(drop=True, inplace=True)
        reg_df.drop(['ID'], axis=1, inplace=True)

        return adjust_read_df_index(reg_df)
    
    except Exception as e:
        print("Error converting regular season data to DataFrame:", e)
        return None

def convert_post_to_df(playoffs_query):
    """Converts playoffs SQL table to viewable pandas DataFrame"""
    try:
        if playoffs_query:
            playoffs_data = [{
                'ID': playoff.id,
                'Season': playoff.season,
                'Team': playoff.team,
                'Pos': playoff.pos,
                'G': playoff.games,
                'PTS': playoff.points,
                'TRB': playoff.rebounds,
                'AST': playoff.assists,
                'STL': playoff.steals,
                'BLK': playoff.blocks,
                'FG%': playoff.fg_percentage,
                'FT%': playoff.ft_percentage,
                '3P%': playoff.three_point_percentage,
                'TOV': playoff.turnovers,
                'MP': playoff.minutes
                 # currently set to None for incomplete data, fix later
            } for playoff in playoffs_query]

            playoffs_df = pd.DataFrame(playoffs_data)

            # sort the playoffs DataFrame by ID and reset index
            playoffs_df.sort_values(by='ID', inplace=True)
            playoffs_df.reset_index(drop=True, inplace=True)
            playoffs_df.drop(['ID'], axis=1, inplace=True)
        else:
            playoffs_df = pd.DataFrame(columns=['Season', 'Team', 'Pos', 'G', 'PTS', 'TRB', 'AST', 'STL', 'BLK'])

        return adjust_read_df_index(playoffs_df)
    
    except Exception as e:
        print("Error converting playoffs data to DataFrame:", e)
        return None

    
def get_player_info(player_query: str) -> dict:
    query = Player.query.filter_by(name=player_query).first()
    
    player_info_dict = {}

    if query:
        player_info = query.player_info
        if player_info:
            player_info_dict = {
                'img_link': player_info.link,
                'position': player_info.positions.split(', ') if player_info.positions else [],
                'teams': player_info.teams.split(', ') if player_info.teams else [],
                'awards': player_info.awards.split(', ') if player_info.awards else [],
                'player_name': player_info.case_name
            }

    return player_info_dict

def query_all_players():
    """Queries all players from the database."""
    try:
        all_players = Player.query.all()
        return all_players
    except Exception as e:
        print("Error retrieving all players:", e)
        return None
    

def delete_player_from_id(player_id: int) -> bool:
    """
    Deletes a player and all related records from the database.
    """
    try:
        PlayerInfo.query.filter_by(player_id=player_id).delete()
        RegularSeason.query.filter_by(player_id=player_id).delete()
        PostSeason.query.filter_by(player_id=player_id).delete()
        MasterPlayer.query.filter_by(player_id=player_id).delete()
        player = Player.query.filter_by(id=player_id).delete()
        
        db.session.commit()
        
        if player:
            print(f"Successfully deleted player with ID {player_id} and all related data.")
            return True
        else:
            print(f"No player found with ID {player_id}.")
            return False

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting player data: {e}")
        return False

def get_position(id) -> list[str]:
    info = PlayerInfo.query.filter_by(player_id=id).first()
    if info:
        return info.positions.split(', ')[0]
    return None

def update_master_player(player_id, reg_stats):
    pos_mapping = {'PG': 1, 'SG': 2, 'SF': 3, 'PF': 4, 'C': 5}
    
    reg_stats = reg_stats[reg_stats['Season']=='Career']
    reg_stats_row = reg_stats.iloc[0]
    pos_str = get_position(player_id)
    pos_num = pos_mapping[pos_str]

    master_player = MasterPlayer.query.filter_by(player_id=player_id).first()
    
    # update the existing entry with the new stats
    if master_player:
        master_player.games = int(reg_stats_row['G'])
        master_player.pos = pos_num
        master_player.points = reg_stats_row['PTS']
        master_player.rebounds = reg_stats_row['TRB']
        master_player.assists = reg_stats_row['AST']
        master_player.steals = reg_stats_row['STL']
        master_player.blocks = reg_stats_row['BLK']
        master_player.turnovers = reg_stats_row['TOV']
        master_player.fg_percentage = reg_stats_row['FG%']
        master_player.three_point_percentage = reg_stats_row['3P%']
        master_player.free_throw_percentage = reg_stats_row['FT%']
        master_player.minutes = reg_stats_row['MP']

        print("updated master table")
        db.session.commit()
    
    else:
        # if no entry exists, create a new one
        new_master_player = MasterPlayer(
            player_id=player_id,
            games=int(reg_stats_row['G']),
            pos=pos_num,
            points=reg_stats_row['PTS'],
            rebounds=reg_stats_row['TRB'],
            assists=reg_stats_row['AST'],
            steals=reg_stats_row['STL'],
            blocks=reg_stats_row['BLK'],
            turnovers=reg_stats_row['TOV'],
            fg_percentage=reg_stats_row['FG%'],
            three_point_percentage=reg_stats_row['3P%'],
            free_throw_percentage=reg_stats_row['FT%'],
            minutes=reg_stats_row['MP']
        )
        print("appended to master table")

        db.session.add(new_master_player)
        db.session.commit()

def query_all_master_table():
    """Queries all players from the master table"""
    try:
        master_all = MasterPlayer.query.all()
        return master_all
    except Exception as e:
        print("Error retrieving all players:", e)
        return None