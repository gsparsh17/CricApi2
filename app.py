from flask import Flask, jsonify, request
import requests
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

BASE_URL = "https://www.crictracker.com/live-scores/"
UPCOMING_URL = "https://www.crictracker.com/live-scores/upcoming/"

def fetch_matches(url):
    response = requests.get(url)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    matches = []
    match_cards = soup.find_all("div", class_="style_fixturesItem__3hcva")
    
    for match in match_cards:
        match_info = {}
        match_info['date_time'] = match.find("p", class_="style_matchTime__pZznE").text.strip()
        match_info['status'] = match.find("p", class_="style_matchStatus__ruEMh").text.strip()
        match_info['format'] = match.find("p", class_="font-semi text-dark").text.strip()
        match_info['venue'] = match.find("p", class_="text-muted").text.strip()
        match_info['tournament'] = match.find("a").text.strip()
        
        teams = match.find_all("div", class_="style_team__FQ6eS")
        if len(teams) == 2:
            match_info['team1'] = teams[0].find("p").text.strip()
            match_info['team2'] = teams[1].find("p").text.strip()
            score1 = teams[0].find_all("p")[1].text.strip()
            score2 = teams[1].find_all("p")[1].text.strip()
            match_info['score1'] = score1 if score1 else "Yet To Bat"
            match_info['score2'] = score2 if score2 else "Yet To Bat"

        # Extracting the scorecard URL
        scorecard_link = match.find("a", string="Scorecard")
        if scorecard_link:
            match_info['scorecard_url'] = "https://www.crictracker.com" + scorecard_link['href']
        else:
            match_info['scorecard_url'] = None

        matches.append(match_info)
    
    return matches

@app.route('/live-matches', methods=['GET'])
def get_live_matches():
    matches = fetch_matches(BASE_URL)
    return jsonify({'live_matches': matches})

@app.route('/upcoming-matches', methods=['GET'])
def get_upcoming_matches():
    matches = fetch_matches(UPCOMING_URL)
    return jsonify({'upcoming_matches': matches})

@app.route('/scrape_scorecard', methods=['GET'])
def scrape_scorecard():
    scorecard_url = request.args.get('url')  # Pass the scorecard link as a query parameter
    if not scorecard_url:
        return jsonify({"error": "Missing scorecard URL"}), 400

    response = requests.get(scorecard_url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch scorecard data"}), 500
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    innings_data = []
    innings_sections = soup.find_all('div', class_='accordion-item')
    
    for innings in innings_sections:
        # Extract Team Name
        team_name_elem = innings.find('div', class_='d-flex')
        team_name = team_name_elem.text.strip() if team_name_elem else "Unknown"
        
        # Extract Batting Data
        score_table = innings.find('table', class_='table')
        if not score_table:
            continue
        
        rows = score_table.find_all('tr')[1:]  # Skip header row
        player_stats = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 6:
                continue  # Skip incomplete rows
            
            # Extract player name and dismissal info
            player_name_elem = cols[0].find('a')
            player_name = player_name_elem.text.strip() if player_name_elem else "Unknown"
            dismissal_info = cols[0].find('span', class_='style_subText__elZ34')
            dismissal = dismissal_info.text.strip() if dismissal_info else "Not out"
            
            runs = cols[1].text.strip()
            balls = cols[2].text.strip()
            fours = cols[3].text.strip()
            sixes = cols[4].text.strip()
            strike_rate = cols[5].text.strip()
            
            player_stats.append({
                "player": player_name,
                "dismissal": dismissal,
                "runs": runs,
                "balls": balls,
                "fours": fours,
                "sixes": sixes,
                "strike_rate": strike_rate
            })
        
        # Extract Fall of Wickets Data
        fall_of_wickets = []
        fall_section = innings.find('div', class_='style_content__R_hNu')
        if fall_section:
            fall_text = fall_section.find('p', class_='text-secondary')
            if fall_text:
                fall_of_wickets = [w.strip() + ")" for w in fall_text.text.strip().split('), ')]
        
        # Extract Bowling Data
        bowler_stats = []
        bowling_table = innings.find_all('table', class_='table')[-1]  # Assuming last table is for bowling
        if bowling_table:
            bowler_rows = bowling_table.find_all('tr')[1:]  # Skip header row
            for row in bowler_rows:
                cols = row.find_all('td')
                if len(cols) < 8:
                    continue
                
                bowler_stats.append({
                    "bowler": cols[0].text.strip(),
                    "overs": cols[1].text.strip(),
                    "maidens": cols[2].text.strip(),
                    "runs": cols[3].text.strip(),
                    "wickets": cols[4].text.strip(),
                    "no_balls": cols[5].text.strip(),
                    "wides": cols[6].text.strip(),
                    "economy": cols[7].text.strip()
                })
        
        innings_data.append({
            "team": team_name,
            "players": player_stats,
            "fall_of_wickets": fall_of_wickets,
            "bowlers": bowler_stats
        })
    
    return jsonify({"scorecard": innings_data})

if __name__ == '__main__':
    app.run(debug=True)
