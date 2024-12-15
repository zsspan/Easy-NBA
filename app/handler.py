"""
Module for handling player data when first initializing and
using the app. Retrieves player information by calling functions
from DB module and accessing various fields
"""

import pandas as pd

from .awards import get_priority_awards
from .comparison import create_comp_df, create_comp_dict
from .data_cleaning import front_end_clean
from .database.db_operations import add_player, convert_reg_to_df, convert_post_to_df, delete_player_from_id, get_player_info, get_player_name, get_player_object, get_player_tables, update_master_player
from .models.BasketballReference import BasketballReference
from .database.data_retrieval import PlayerInfo
from .similarity import get_closest_player, get_similarity_score


def handle_player_data(user_input) -> tuple:
    player_lower = user_input.lower()
    player_obj = get_player_object(player_lower)
    # player already in DB, READ
    if player_obj:
        print("Player is already in the database")
        reg_query, playoffs_query = get_player_tables(player_obj)
        reg, playoffs = convert_reg_to_df(reg_query), convert_post_to_df(playoffs_query)
        player_info = get_player_info(player_lower)
        # new
        player_info['priority_awards'] = get_priority_awards(player_info['awards'])
        # update_master_player(player_obj.id, reg) #for manual update

    # player not in DB, WRITE
    elif not player_obj:
        try:
            player_cleaned = user_input.replace("'", "").lower().split()
            player_cleaned = player_cleaned[0] + "_" + player_cleaned[1]
            player_raw = BasketballReference(user_input)
            player = PlayerInfo(player_raw)
            reg, playoffs = player.reg, player.post
            player_info = player.get_player_info()
            # new
            player_info['priority_awards'] = get_priority_awards(player_info['awards'])
            
            if not player_obj:
                print("Player is NEW")
                add_player(player_lower, reg, playoffs, player_info)
                player_obj = get_player_object(player_lower)

                update_master_player(player_obj.id, reg)
                # print(player_obj.id)
            
        except Exception as e:
            print("Sorry, the player couldn't be found:", e)
            return None
    
    reg, playoffs = front_end_clean(reg), front_end_clean(playoffs)
    return player_obj, reg, playoffs, player_info


def handle_closest_player(id: int) -> str:
    if id is None:
        return None
    closest_players, scores = get_closest_player(id)
    return closest_players


def handle_deletion_status(id: int) -> list[str, bool]:
    p_name = get_player_name(id)
    return [p_name, delete_player_from_id(id)]

# handles /compare, returns player dictionaries and aggregate dfs
def handle_comparison(p1: str, p2: str) -> dict:
    p1_info, p2_info = {}, {}
    comp_df1, comp_df2 = None, None

    p1_recv = handle_player_data(p1)
    p2_recv = handle_player_data(p2)

    # conditionally get players
    if p1_recv and p2_recv:
        # player 1 stuff
        p1_obj, reg1, playoffs1, p1_info = p1_recv
        df1 = reg1[reg1['Season']=='Career']
        
        df2 = pd.DataFrame()
        if not playoffs1.empty:
            df2 = playoffs1[playoffs1['Season']=='Career']
        
        comp_df1 = create_comp_df(df1, df2)

        # player 2 stuff
        p2_obj, reg2, playoffs2, p2_info = p2_recv
        df1 = reg2[reg2['Season']=='Career']
        
        df2 = pd.DataFrame()
        if not playoffs2.empty:
            df2 = playoffs2[playoffs2['Season']=='Career']            
        
        comp_df2 = create_comp_df(df1, df2)

        score = get_similarity_score(p1_obj.id, p2_obj.id)

    return p1_info, p2_info, comp_df1, comp_df2, score

def handle_comp_dict(comp_df1: pd.DataFrame, comp_df2: pd.DataFrame) -> tuple[dict,dict]:
    if comp_df1 is None or comp_df2 is None:
         return {}, {}
    return create_comp_dict(comp_df1, comp_df2)