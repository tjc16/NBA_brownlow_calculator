# calculator module

import streamlit as st
import pandas as pd


try:
    rs_df = pd.read_csv("playerstatistics.csv")
except FileNotFoundError:
    st.error("File not found. Please upload 'playerstatistics.csv' or check the path.")
    st.stop()

# a) data frame
rs_df = df[df['gameType'] == 'Regular Season'].copy()

# b) player full name
rs_df['player_name'] = rs_df['firstName'] + ' ' + rs_df['lastName']

# c) season
rs_df['gameDate'] = pd.to_datetime(rs_df['gameDate'])

def infer_season(dt):
    if dt.month >= 9:        # Sept–Dec
        season_year = dt.year + 1
    else:                    # Jan–Jun (and earlier months, if present)
        season_year = dt.year
    return str(season_year)

rs_df['season'] = rs_df['gameDate'].apply(infer_season)


st.title("Brownlow Vote Calculator")

st.sidebar.header("Custom Weights")
points = st.sidebar.slider("points", 0.0, 5.0, 1.0)
assists = st.sidebar.slider("assists", 0.0, 5.0, 2.0)
blocks = st.sidebar.slider("blocks", 0.0, 5.0, 3.0)
steals = st.sidebar.slider("steals", 0.0, 5.0, 2.0)
FieldGoalsAttempted = st.sidebar.slider("fieldGoalsAttempted", -2.0, 0.0, -0.7)
FieldGoalsMade = st.sidebar.slider("fieldGoalsMade", 0.0, 4.0, 2.0)
ThreePointersMade = st.sidebar.slider ("threePointersMade", 0.0, 3.0, 0.75)
FreeThrowsAttempted = st.sidebar.slider ("freeThrowsAttempted", -2.0, 0.0, -0.3)
FreeThrowsMade = st.sidebar.slider ("freeThrowsMade", 0.0, 2.0, 0.75)
reboundsdefensive = st.sidebar.slider ("reboundsdefensive", 0.0, 3.0, 1.0)
reboundsoffensive = st.sidebar.slider ("reboundsoffensive", 0.0, 5.0, 1.25)
turnovers = st.sidebar.slider ("turnovers", -5.0, 0.0, -1.0)
personalfouls = st.sidebar.slider ("foulsPersonal", -5.0, 0.0, 0.0)
plusminus = st.sidebar.slider ("plusMinusPoints", 0.0, 1.0, 0.3)
WinMultiplier = st.sidebar.slider ("Win Multiplier", 0.0, 3.0, 1.25)



# Create score using weights

WEIGHTS = {
    'points': points,
    'assists': assists,
    'blocks': blocks,
    'steals': steals,
    'fieldGoalsAttempted': FieldGoalsAttempted,
    'fieldGoalsMade': FieldGoalsMade,
    'threePointersMade': ThreePointersMade,
    'freeThrowsAttempted': FreeThrowsAttempted,
    'freeThrowsMade': FreeThrowsMade,
    'reboundsDefensive': reboundsdefensive,
    'reboundsOffensive': reboundsoffensive,
    'turnovers': turnovers,
    'foulsPersonal':personalfouls,
    'plusMinusPoints': plusminus,
        }
WIN_MULTIPLIER = WinMultiplier


weights = pd.Series(WEIGHTS)

rs_df['raw_score'] = rs_df[list(WEIGHTS.keys())].dot(weights)
rs_df['score'] = rs_df['raw_score'] * rs_df['win'].replace({0: 1, 1: WIN_MULTIPLIER})

# assign votes
def assign_votes(group):
    # Sort by score descending
    group = group.sort_values('score', ascending=False)

    # Define vote values
    base_votes = [3, 2 ,1]
    
    # Only assign as many votes as there are players
    votes = base_votes[:len(group)] + [0] * max(0, len(group) - len(base_votes))
    
    group['votes'] = votes
    return group

# Apply function to each game
rs_df = rs_df.groupby('gameId', group_keys=False).apply(assign_votes)

# Ensure votes are integers
rs_df['votes'] = rs_df['votes'].astype(int)

# vote aggregation and display

rs_df['season_total_votes'] = (
rs_df
    .groupby(['season', 'player_name'])['votes']
    .transform('sum')
)

# output table
season_player_votes = (
    rs_df
    .groupby(['season', 'player_name'], as_index=False)['votes']
    .sum()
    .rename(columns={'votes': 'season_total_votes'})
)

# top 5 per season
top5_per_season = (
    season_player_votes
      .sort_values(['season', 'season_total_votes'], ascending=[True, False])
      .groupby('season')
      .head(5)
)

# ranks
top5_per_season['rank'] = top5_per_season.groupby('season')['season_total_votes'].rank(method='first', ascending=False).astype(int)


st.dataframe(top5_per_season)
