import pandas as pd

from sklearn import linear_model
from sklearn.model_selection import train_test_split

from flask import Flask, render_template, redirect, url_for, session

from forms import GetScoreData

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# Load dataframe
score_data = pd.read_csv(f"static/arrow_scores_summer_23.csv", header = 0)

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

# Create dataframe column converting the datetime object to a day of week string
score_data["day_of_week"] = score_data.date.dt.day_of_week

# .groupby() the desired columns
# Select only the columns to display
# Create dataframe with mean values
# Create dataframe with .count() of single column
# Merge the dataframes into one
# Print

# OR

# .groupby() the desired columns
# Select only the columns to display
# Create a dataframe with mean values
# Print

# Display the trends depending on day of week
day_of_week = score_data.groupby(score_data.day_of_week)
day_of_week_cols = day_of_week[['arrow_average','arrows','golds_pct']]
day_of_week_summary = day_of_week_cols.mean()
day_of_week_count = score_data.groupby(score_data.day_of_week)['date'].count()
day_of_week_merged = day_of_week_summary.merge(day_of_week_count, on=["day_of_week"])
print(f"\n\nScore Data grouped by Day of Week: \n{day_of_week_merged}\n")

# Display the trends depending on month and year
month_and_year = score_data.groupby(
    [score_data.date.dt.year, score_data.date.dt.month])
month_and_year_cols = month_and_year[['arrow_average','distance','arrows','golds_pct']]
month_and_year_summary = month_and_year_cols.mean()
print(f"Score Data grouped by Month: \n{month_and_year_summary}\n")

# Display the trends depending on month and year ALSO seperated by Distance to target
month_year_dist = score_data.groupby(
    [score_data.distance, score_data.date.dt.year, score_data.date.dt.month] )
month_year_dist_cols = month_year_dist[['arrow_average','arrows','golds_pct']]
month_year_dist_summary = month_year_dist_cols.mean()
print(f"Score Data grouped by Distance by Month: \n{month_year_dist_summary}\n")

# Display the trends depending on distance
dist = score_data.groupby(['distance'])
dist_cols = dist[['arrow_average','arrows','golds_pct']]
dist_summary = dist_cols.mean()
print(f"Score Data grouped by Distance: \n{dist_summary}\n")

# Display the trends depending on whether or not the shoot was at a competition
dist_comp = score_data.groupby([score_data.distance, score_data.is_comp])
dist_comp_cols = dist_comp[['arrow_average','arrows','golds_pct']]
dist_comp_summary = dist_comp_cols.mean()
print(f"Score Data grouped by Competition Status: \n{dist_comp_summary}\n")

# Select features to predict FROM and features to predict TO
features = score_data[["distance","days_since_first_entry","is_comp"]]
scored = score_data[["arrow_average","golds_pct"]]

# Split the data into training and testing subsets
# This ensures there is 'real' data left unseen by the model which can be 
# used to score the models accuracy.
# THERE IS A DANGER HERE: if the 20% testing subset includes the very few datapoints with
# "is_comp" equal to 1 then the model will have no values to train this feature on.
# To resolve this issue I need more data, however this is obviously easier said than done...
X_train, X_test, y_train, y_test = train_test_split(
    features, scored, test_size = 0.2, random_state = 864)
# Creates the LinReg model and trains it with the training subset
model = linear_model.LinearRegression()
model.fit(X_train, y_train)

# Score the model
# This is done on training AND testing data to highlight overfitting
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
print(f"Train Model Score: {train_score}")
print(f"Test Model Score: {test_score}\n")

# print(f"\n{score_data.groupby(['distance', 'is_comp']).mean()}\n")
    
@app.route('/', methods=["GET","POST"])
def index():
    get_score_data = GetScoreData()
    # On submission...
    if get_score_data.validate_on_submit():
        # Getters for form data
        distance = get_score_data.distance.data
        days_till = get_score_data.days_till.data
        is_comp = get_score_data.is_comp.data
        
        # Sanitise input
        distance, days_till = float(distance), float(days_till)
        
        # Use the trained model to predict output variables from input variables
        # max(score_data.days_since_first_entry) + days_till 
        # --> Most recent entry to .csv file + user specified number of days
        guesses = model.predict(
            [[distance, 
              max(score_data.days_since_first_entry) + days_till, 
              is_comp]]
        )
        
        # Sanitise output
        # Max possible score is 10
        # Max gold_pct is 100%
        if guesses[0][0] > 10:
            guesses[0][0] == f"10.00 {guesses[0][0]}"
        if guesses[0][1] > 100:
            guesses[0][1] = 100

        # Save vars to server-side-stored session data
        session["distance"] = distance
        session["days_till"] = days_till
        session["avg_score"] = guesses[0][0]
        session["gold_pct"] = guesses[0][1]
        session["is_comp"] = is_comp
        
        # Redirect to the 'submitted' path
        return redirect(url_for(
            'submitted',
            _external=True, 
            scheme='https'
        ))
     
    return render_template(
        "index.html", 
        get_score_data=get_score_data, most_recent_date = most_recent_date
    )

@app.route('/submitted', methods=["GET","POST"])
def submitted():
    # Retrieve vars from server-side-stored session data
    distance = session["distance"]
    days_till = session["days_till"]
    avg_score = session["avg_score"]
    gold_pct = session["gold_pct"]
    is_comp = session["is_comp"]
    
    # Pass all template vars in here
    return render_template(
        "submit.html",
        distance = distance,
        days_till = days_till,
        avg_score = f"{avg_score:.3f}",
        gold_pct = f"{gold_pct:.2f}",
        is_comp = is_comp,
        _external=True, _scheme='https')

# PLOTTING
from matplotlib import pyplot as plt
import seaborn as sns
print("plotting")

# Figure labels
plt.xlabel("Distance")
plt.ylabel("Average Arrow Score")

# Colour Map used to differentiate days of week or by month
cmap_seven = plt.cm.get_cmap('cool', 7)
cmap_twelve = plt.cm.get_cmap('cool', 12)

# Scatterplot of distance against arrow average
# Style: O markers if not competition, X markers if is competition
# Hue: Change colour of marker depending on day of week of shoot, uses 'cmap' to discern colours
def plot_by(hue_type, label, cmap):
    sns.scatterplot(
        data = score_data,
        x = "distance", y = "arrow_average",
        style = "is_comp",
        hue = hue_type,
        palette = cmap,
    )

    # Plot lines for min / avg / max arrow scores at each distance
    plt.plot(score_data.distance.unique(), score_data.groupby(['distance']).max().arrow_average, "k:")
    plt.plot(score_data.distance.unique(), score_data.groupby(['distance']).mean().arrow_average, "g--")
    plt.plot(score_data.distance.unique(), score_data.groupby(['distance']).min().arrow_average, "k:")
    
    plt.show(block=False)
    plt.savefig(f"{label}_fig.png")
    plt.clf()

plot_by(score_data.day_of_week, "day_of_week", cmap_seven)    
plot_by(score_data.date.dt.month, "month", cmap_twelve)

sns.scatterplot(
    data = score_data,
    x = "date", y = "arrow_average",
    style = "is_comp",
    hue = "distance",
    palette = plt.cm.get_cmap('tab20'),
)
plt.savefig("distance_fig.png")
plt.clf()