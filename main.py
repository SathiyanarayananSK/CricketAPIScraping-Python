# Importing requests for scraping the APIs and pandas for constructing and building csv
import requests
import pandas as pd

# Default header to imitate browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Referer": "https://www.foxsports.com.au/",
}


# Function to find the total number of innings from match details API
def find_total_innings():
    url_match_details = "https://statsapi.foxsports.com.au/3.0/api/sports/cricket/matches/BBL2024-250101/details.json?userkey=C2AC830D-9933-44C0-8E40-32DF637CD1AB"
    response_md = requests.get(url_match_details, headers=headers)
    data_md = response_md.json()
    return data_md["end_of_day_list"][0]["innings"]

# Function to get ball-by-ball data based on innings
def ball_by_ball_details(inning_num):
    url_ball_by_ball = f"https://statsapi.foxsports.com.au/3.0/api/sports/cricket/matches/BBL2024-250101/innings/{inning_num}/fullballbyball.json?userkey=C2AC830D-9933-44C0-8E40-32DF637CD1AB"
    response_byb = requests.get(url_ball_by_ball, headers=headers)
    data_byb = response_byb.json()
    return data_byb

# Function to check how the player got out based on inning number and player_id using batting-score-card API
def player_how_out(out_inning, player_id):
    url_batting_scorecards = f"https://statsapi.foxsports.com.au/3.0/api/sports/cricket/matches/BBL2024-250101/innings/{out_inning}/battingscorecards.json?userkey=C2AC830D-9933-44C0-8E40-32DF637CD1AB"
    response_sc = requests.get(url_batting_scorecards, headers=headers)
    data_sc = response_sc.json()

    # Initially setting how_out variables to none
    local_how_out = None
    local_how_out_description = None

    # Looping through each player and setting values to how_out variables
    for player in data_sc:
        if player["id"] == player_id:
            local_how_out = player["how_out"]
            local_how_out_description = player["how_out_description"]
    return  local_how_out, local_how_out_description

# Function to construct a csv based on a list using pandas
def construct_csv(list_data):
    df = pd.DataFrame(list_data)
    df.to_csv('Ball_by_ball_data.csv', index=False)


if __name__ == "__main__":
    # Set number of innings
    innings = find_total_innings()
    # Initiate a list that stores each ball data as a dictionary
    ball_by_ball_data = []

    # Loop through the number of innings
    for inning in range(innings):
        # Add 1 -> as the range value starts from 0
        inning +=1

        # Get the data by calling the function
        data = ball_by_ball_details(inning)

        # Loop through each ball's data to make it into the desired format
        for ball in data:
            ball_data = {}
            for key, value in ball.items():
                # Check if the value is dict, if yes, handle it
                if isinstance(value, dict) :
                    # Handle dictionary values
                    for name, detail in ball[key].items():
                        new_name = f"{key}_{name}"
                        ball_data[new_name] = detail

                        # Get how the Batsman got out from a different API using player_how_out function
                        if new_name == "dismissedBatsman_id":
                            if detail is not None:
                                how_out, how_out_description = player_how_out(out_inning=inning, player_id=detail)
                                ball_data["how_out"] = how_out
                                ball_data["how_out_description"] = how_out_description
                            else:
                                ball_data["how_out"] = None
                                ball_data["how_out_description"] = None
                else:
                    # Add the clean data to the dictionary
                    ball_data[key] = value

            # Append the ball_data dictionary to the list
            ball_by_ball_data.append(ball_data)

    # Construct a csv based on ball_by_ball_data list
    construct_csv(list_data=ball_by_ball_data)



