# Flask Imports
from flask import Flask, render_template, request, redirect, url_for
from forms import GetScoreData
# Pandas - dataframe management
import pandas as pd
# Datetime - used to get todays date
from datetime import date
# Auto-open web browser to page
import webbrowser
# Used to check for 'nan' values
import math

PATH = "static/scores.csv"

# Flask setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

event = "TESTING EVENT"
event = input("Event Name: ").title().rstrip()

# Get date, format into DD/MM/YYYY
today = date.today().strftime("%d/%m/%Y")

@app.context_processor
def set_event():
    return dict(event_name=event, date=today)

# Open the flask app in a web browser
# Home IP, Port 5000
webbrowser.open("http://127.0.0.1:5000/")

# "Index" Route / Homepage
# Read and process data from csv file
# Sort by highest score and convert to a list
# Display in table format using template "index.html"
@app.route('/', methods=["GET","POST"])
def index():
    score_data = pd.read_csv(PATH)
    score_data = score_data.sort_values(by=["score"], ascending=False)
    
    count = score_data.shape[0]
    avg_score = score_data.score.mean()
    if math.isnan(avg_score): avg_score = 0
    
    score_data = score_data.values.tolist()
    
    return render_template(
        "index.html", 
        score_data=score_data,
        count=count,
        avg_score=avg_score
    )

# "Add Score" Route
# Create an instance of the form "GetScoreData"
# When form is submitted from "add_score.html" template, save data to 
# corresponding variables.
# Write the data to the csv file
# Return to the index route to display data
@app.route('/add_score', methods=["GET","POST"])
def add_score():
    get_score_data = GetScoreData()
    if get_score_data.validate_on_submit():
        name = get_score_data.name.data
        score = get_score_data.score.data
        age_category = get_score_data.age_category.data
        sex = get_score_data.sex.data
        email = get_score_data.email.data
        phone_num = get_score_data.phone_num.data
        
        with open(PATH, "a") as score_file:
            line = f"{name},{score},{age_category},{sex},{email},{phone_num}\n"
            score_file.write(line)
            
        return redirect(url_for(
            "index", _external=True, scheme="https"
        ))
        
    return render_template(
        "add_score.html", get_score_data=get_score_data
    )

# How many names to display:
N_WINNERS = 3

# Helper function that gets the top 3 scores in the grouped data and returns
# them as a list in the format [["Name", score], ]
def grouper(grouped_data, name):
    try:
        lst = grouped_data.get_group(name).head(N_WINNERS).values.tolist()
    except KeyError:
        lst = [["",""]]
        print(f"{name} list empty.")
    return lst

# 'Results' Route
# Get the top 'N_WINNERS' number of scores, grouped by:
# All entries, Age category, Gents / Ladies
# Display each set of results in
@app.route('/results', methods=["GET","POST"])
def results():
    score_data = pd.read_csv(PATH)
    score_data = score_data.sort_values(by=["score"], ascending=False)
    
    overalls = score_data[["name","score"]].head(N_WINNERS).values.tolist()
    if len(overalls) == 0: overalls = [["",""]] # If data empty
    
    age_grouped = score_data.groupby(score_data.age_category)
    seniors = grouper(age_grouped, "Senior")
    juniors = grouper(age_grouped, "Junior")
        
    sex_grouped = score_data.groupby(score_data.sex)
    gents = grouper(sex_grouped, "Gents")
    ladies = grouper(sex_grouped, "Ladies")
    
    return render_template(
        "results.html",
        overalls=overalls,
        seniors=seniors,
        juniors=juniors,
        gents=gents,
        ladies=ladies
    )