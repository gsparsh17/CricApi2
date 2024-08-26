from flask import Flask, render_template_string, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

# Example HTML content
app = Flask(__name__)
CORS(app)

@app.route('/api/upcoming-matches', methods=['GET'])
def recent_scores():
#       url = 'https://www.crictracker.com/live-scores/recent/'
#       response = requests.get(url)

#       soup = BeautifulSoup(response.content, 'html.parser')

# # Find all matches
#       match_time = soup.find('p', class_='style_matchTime__pZznE').text

# # Extract the match result
#       match_result = soup.find('p', class_='d-flex align-items-start style_matchStatus__ruEMh text-success').text.strip()

# # Extract the match type and location
#       match_type = soup.find('p', class_='font-semi text-dark').text
#       location = soup.find('p', class_='text-muted').text

# # Extract the team names and scores
#       teams = soup.find_all('div', class_='style_team__FQ6eS')
#       team1_name = teams[0].find('p').text
#       team1_score = teams[0].find_all('p')[1].text
#       team2_name = teams[1].find('p').text
#       team2_score = teams[1].find_all('p')[1].text

# # Print the extracted information
#       data={
#     "match_time": match_time,
#     "result": match_result,
#     "match_type": match_type,
#     "location": location,
#     "teams": [
#         {
#             "name": team1_name,
#             "score": team1_score
#         },
#         {
#             "name": team2_name,
#             "score": team2_score
#         }
#               ]
#              }

#       print(f"Match Time: {match_time}")
#       print(f"Result: {match_result}")
#       print(f"Match Type: {match_type}")
#       print(f"Location: {location}")
#       print(f"{team1_name}: {team1_score}")
#       print(f"{team2_name}: {team2_score}")
#       return jsonify(data)

 url = "https://www.crictracker.com/live-scores/upcoming/"

# Fetch the page content
 response = requests.get(url)
 html_content = response.content

# Parse the HTML content
 soup = BeautifulSoup(html_content, 'html.parser')

# Find all match cards
 match_cards = soup.find_all('div', class_='style_fixturesItem__3hcva')

# List to store match data
 matches = []

# Loop through each match card and extract data
 for card in match_cards:
      match_time = card.find('p', class_='style_matchTime__pZznE').text.strip()
    #   match_result = card.find('p', class_='d-flex align-items-start style_matchStatus__ruEMh text-success').text.strip()
      match_type = card.find('p', class_='font-semi text-dark').text.strip()
      location = card.find('p', class_='text-muted').text.strip()

      teams = card.find_all('div', class_='style_team__FQ6eS')
      team1_name = teams[0].find('p').text.strip()
      team1_score = teams[0].find_all('p')[1].text.strip()
      team2_name = teams[1].find('p').text.strip()
      team2_score = teams[1].find_all('p')[1].text.strip()

      match_data = {
        "match_time": match_time,
        "match_type": match_type,
        "location": location,
        "teams": [
            {
                "name": team1_name,
            },
            {
                "name": team2_name,
            }
        ]
    }
      matches.append(match_data)
 return matches

def get_recent_matches():
    matches = recent_scores()
    return jsonify(matches)

if __name__ == '__main__':
    app.run(debug=True, port=8080)