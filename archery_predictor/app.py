import pandas as pd

from sklearn import linear_model
from sklearn.model_selection import train_test_split

from flask import Flask, render_template, redirect, url_for, session

from forms import GetScoreData

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# Load dataframe
score_data = pd.read_csv("static/archery.csv", header = 0)

# Convert the date column from objects to datetypes 
score_data.date = pd.to_datetime(score_data.date)

# Create a column of the calculated percent of gold arrows (arrows scoring 9)
score_data["golds_pct"] = (score_data.golds / score_data.arrows)*100

# Create a column indicating the time elapsed since the first entry
# This is used as a feature to show progress over time
score_data["days_since_first_entry"] = (
    score_data.date - min(score_data.date) ).dt.days

# Get the most recent entry to the .csv file.
# This is displayed in "index.html" for the user to calculate the desired 
# days till feature since this date.
most_recent_date = max(score_data.date).strftime("%Y-%m-%d")

# Select features to predict FROM and features to predict TO
features = score_data[["distance","days_since_first_entry","is_comp"]]
scored = score_data[["arrow_average","golds_pct"]]

X_train, X_test, y_train, y_test = train_test_split(
    features, scored, test_size = 0.2, random_state = 123)

model = linear_model.LinearRegression()
model.fit(X_train, y_train)

train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
print(f"Train Model Score: {train_score}")
print(f"Test Model Score: {test_score}\n")

# print(f"\n{score_data.groupby(['distance', 'is_comp']).mean()}\n")
    
@app.route('/', methods=["GET","POST"])
def index():
    get_score_data = GetScoreData()
    if get_score_data.validate_on_submit():
        distance = get_score_data.distance.data
        days_till = get_score_data.days_till.data
        is_comp = get_score_data.is_comp.data
        
        distance, days_till = float(distance), float(days_till)
        
        guesses = model.predict([[distance, max(score_data.days_since_first_entry) + days_till, is_comp]])
        
        if guesses[0][0] > 10:
            guesses[0][0] == f"10.00 {guesses[0][0]}"
        if guesses[0][1] > 100:
            guesses[0][1] = 100

    
        session["distance"] = distance
        session["days_till"] = days_till
        session["avg_score"] = guesses[0][0]
        session["gold_pct"] = guesses[0][1]
        session["is_comp"] = is_comp
        
        return redirect(url_for(
            'submitted',
            _external=True, 
            scheme='https'
        ))
     
    return render_template("index.html", get_score_data=get_score_data, most_recent_date = most_recent_date)

@app.route('/submitted', methods=["GET","POST"])
def submitted():
    
    distance = session["distance"]
    days_till = session["days_till"]
    avg_score = session["avg_score"]
    gold_pct = session["gold_pct"]
    is_comp = session["is_comp"]
    
    return render_template( # should use redirect here but wouldnt work oops
        "submit.html",
        distance = distance,
        days_till = days_till,
        avg_score = f"{avg_score:.3f}",
        gold_pct = f"{gold_pct:.2f}",
        is_comp = is_comp,
        _external=True, _scheme='https')
    
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
print("plotting")

score_data["day_of_week"] = score_data.date.dt.day_of_week

# score_data.day_of_week = score_data.day_of_week.map(
#     {0:"Monday",1:"'Tuesday'",2:"Wednesday",3:"Thursday",4:"'Friday'",
#      5:"Saturday",6:"'Sunday'"} )
# score_data.day_of_week = pd.Categorical(
#     score_data.day_of_week, 
#     # ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
#     ["Tuesday","Friday","Sunday"]) # Shooting days only

plt.xlabel("Distance")
plt.ylabel("Average Arrow Score")

cmap = ListedColormap(["red", "orange", "yellow", "green", "blue", "indigo", "violet"])
hue_order = [0,1,2,3,4,5,6]

sns.scatterplot(
    data = score_data,
    x = "distance", y = "arrow_average",
    style = "is_comp",
    hue = "day_of_week",
    palette = cmap
)

plt.plot(score_data.distance.unique(), score_data.groupby(['distance']).max().arrow_average, "k:")
plt.plot(score_data.distance.unique(), score_data.groupby(['distance']).mean().arrow_average, "g--")
plt.plot(score_data.distance.unique(), score_data.groupby(['distance']).min().arrow_average, "k:")

plt.show(block=False)
plt.savefig("fig.png")