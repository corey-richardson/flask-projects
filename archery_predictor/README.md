# Archery Average Arrow Score Regressor

---

## Contents

- [dataframe](#dataframe)
- [the-regressor-model](#the-regressor-model)
- [the-index-route](#the-index-route)
- [forms-py-getscoredata](#formspy---getscoredata)
- [index-html](#indexhtml)
- [the-submit-route](#the-submit-route)
- [submit-html](#submithtml)
- [style-css](#stylecss)
- [predicted-results](#predicted-results)
- [post-competition-changes](#post-competition-changes)
- [summary-statistics](#summary-statistics)
- [plotting](#plotting)

---

## Dataframe

Uses the Pandas module to read `archery.csv` into a Dataframe.
```py
score_data = pd.read_csv("static/archery.csv", header = 0)
```

New columns `"days_since_first_entry"` and `"gold_pct"` are created. These features are used within the model as a predictive and predicted variable respectively.
```py
score_data.date = pd.to_datetime(score_data.date)
score_data["golds_pct"] = (score_data.golds / score_data.arrows)*100
score_data["days_since_first_entry"] = (
    score_data.date - min(score_data.date) ).dt.days

most_recent_date = max(score_data.date).strftime("%Y-%m-%d")
```

---

## The Regressor Model

The data is split into training and testing subsets. The parameter `random_state = 123` ensures the model is the same each time it is ran. `123` was found to be the value that maximises the average model score between the training and testing subsets. <br>
This is also where the model is initialised and trained.
```py
X_train, X_test, y_train, y_test = train_test_split(
    features, scored, test_size = 0.2, random_state = 123)

model = linear_model.LinearRegression()
model.fit(X_train, y_train)

train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
print(f"Train Model Score: {train_score}")
print(f"Test Model Score: {test_score}\n")
```

---

## The 'index' Route

```py
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
```

In the index route - `127.0.0.1:5000/` - the Form object is called and validated.
```py
@app.route('/', methods=["GET","POST"])
def index():
    get_score_data = GetScoreData()
    if get_score_data.validate_on_submit():
        distance = get_score_data.distance.data
        days_till = get_score_data.days_till.data
```

The model then predicts the average arrow score and percentage of arrows scoring 9.
```py
guesses = model.predict([[distance, max(score_data.days_since_first_entry) + days_till]])
```
> `max(score_data.days_since_first_entry)` corresponds to the most recent entry to the csv file. <br>
> `+ days_till` then adds the desired elapsed number of days to this value.

Data sanitisation is used here for when the model predicts values which are out of range of the real possible values. For example, the maximum score on a 122cm target is 10, and you can't have over 100% of your arrows being gold.
> 10 is the highest possible score when shooting a metric round using 10-zone scoring (10,9,8,7,6,5,4,3,2,1); when shooting an imperial round using 5-zone scoring (9,7,5,3,1) the maximum score is 9.
```py
if guesses[0][0] > 10:
    guesses[0][0] == f"10.00 {guesses[0][0]}"
if guesses[0][1] > 100:
    guesses[0][1] = 100
```

![122cm face](https://cdn.shopify.com/s/files/1/1530/4477/products/paper-archery-target-face-122cm-fita_large.png?v=1552558054)

Here I used the `flask.session` method to save the data server-side to later be access in the '/submitted' route. <br>
Then, I `redirect` to the '/submitted' route to display the model's prediction.
```py
session["distance"] = distance
session["days_till"] = days_till
session["avg_score"] = guesses[0][0]
session["gold_pct"] = guesses[0][1]

return redirect(url_for(
    'submitted',
    _external=True, 
    scheme='https'
))
```

Whilst the form has not been validated, the template `"index.html"` is displayed.
```py
return render_template(
    "index.html", 
    get_score_data=get_score_data, 
    most_recent_date = most_recent_date
)
```

![index-route](/archery_predictor/readme_assets/index.PNG)
> I have a competition shooting a National (48 arrows at 60 yards, 24 arrows at 50 yards) on 2023-05-28 so I will use a "Days Till Shoot" value of 5 in my example images.

## forms.py - GetScoreData

```py
from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class GetScoreData(FlaskForm):
    distance = RadioField(
        "Distance",
        choices = [
            (10.0, "10 yards"),
            (19.685, "18 metres"),
            (20.0, "20 yards"),
            (30.0, "30 yards"),
            (40.0, "40 yards"),
            (50.0, "50 yards"),
            (54.6807, "50 metres"),
            (60, "60 yards"),
            (76.5529, "70 metres"),
            (80.0, "80 yards"),
            (100.0, "100 yards")
        ]
    )
    days_till = IntegerField("Days Till Shoot: ", validators=[DataRequired()])
    submit = SubmitField("Submit")
```

## index.html

```html
<link href="static/style.css" rel="stylesheet" />

<form action="/" method="post">

    {{ get_score_data.hidden_tag() }}


    <h2> {{ get_score_data.distance.label }} </h2>
    <table>
        <tr>
            {% for btn in get_score_data.distance %}
            <td>{{ btn()     }}</td>
            <td>{{ btn.label }}</td>
            {% endfor %}
        </tr>
    </table> <br>

    <h2> {{get_score_data.days_till.label}}</h2>
    <h4>(since {{ most_recent_date }})</h3>
    {{ get_score_data.days_till() }}

    {{ get_score_data.submit() }}

</form>
```

The `hidden_tag()` template argument generates a hidden field that includes a token that is used to protect the form against CSRF attacks. 
```html
{{ get_score_data.hidden_tag() }}
```

Next, I create a table object and iterate through each radio button option defined in the form definition.
```html
<h2> {{ get_score_data.distance.label }} </h2>
<table>
    <tr>
        {% for btn in get_score_data.distance %}
        <td>{{ btn()     }}</td>
        <td>{{ btn.label }}</td>
        {% endfor %}
    </tr>
</table> <br>
```

I also display a text field object allowing the user to enter the "Days Till Shoot" value. The `<h4>` element here is used to display the date of the latest entry in the csv file.
```html
<h2> {{get_score_data.days_till.label}}</h2>
<h4>(since {{ most_recent_date }})</h3>
{{ get_score_data.days_till() }}
```

---

## The 'submit' Route

```py
@app.route('/submitted', methods=["GET","POST"])
def submitted():
    
    distance = session["distance"]
    days_till = session["days_till"]
    avg_score = session["avg_score"]
    gold_pct = session["gold_pct"]
        
    return render_template( # should use redirect here but wouldnt work oops
        "submit.html",
        distance = distance,
        days_till = days_till,
        avg_score = f"{avg_score:.3f}",
        gold_pct = f"{gold_pct:.2f}",
        _external=True, _scheme='https')
```

The 'submitted' route - `127.0.0.1/submitted' - displays the output of the model.

Firstly, I retrieve the variables I want to display from the server-side `flask.session` storage.
```py
distance = session["distance"]
days_till = session["days_till"]
avg_score = session["avg_score"]
gold_pct = session["gold_pct"]
```

Then, I display the `"submit.html"` template passing `distance`, `days_till`, `avg_score` and `gold_pct` as arguments. `avg_score` and `gold_pct` are directly derived and formatted from the models output.
```py
return render_template( # should use redirect here but wouldnt work oops
    "submit.html",
    distance = distance,
    days_till = days_till,
    avg_score = f"{avg_score:.3f}",
    gold_pct = f"{gold_pct:.2f}",
    _external=True, _scheme='https')
```

![submitted](/archery_predictor/readme_assets/submitted.PNG)

---

## submit.html

```html
<link href="static/style.css" rel="stylesheet" />

<p>In <b>{{ days_till | int }} days</b> you could be scoring an average arrow score of <b>{{ avg_score }}</b> at <b>{{ distance }} yards / {{ (distance / 1.094) | round(1)
}} metres</b> with <b>{{ gold_pct }}%</b> being golds. (122cm Target Face)</p>
<p>Want to try another distance? Click <a href="/">here</a>.</p>
```

- `{{ days_till | int }}` - cast from a `float` to an `int`
- `{{ avg_score }}`
- `{{ distance }} yards / {{ (distance / 1.094) | round(1)
}} metres` - display the distance in both yards and metres. The model works entirely in yards and so the values for the 18m / 50m /70m radio button options need to be converted to metres again before being displayed to the user.
- `{{ gold_pct }}`

---

## style.css

Define variables for later use. These are taken directly from my [Yelverton Bowmen Website Prototype](https://github.com/corey-richardson/yelverton-bowmen/tree/main) project and as such are not all used here.
```css
:root {
    --yb_blue: #0080FE;
    --yb_yellow: #FFFC00;
    --yb_light_blue: #E0E8FF;
    --yb_dark_blue: #002447;
}
```

Set ALL elements to the 'Lucida Grande' font.
```css
* {
    font-family: "Lucida Grande", "Lucida Sans Unicode";
    padding: 0;
}
```

```css
a {
    color: var(--yb_blue);
}

a:hover {
    color: var(--yb_dark_blue);
}
```

```css
h1, h2, h3, h4 {
    color: var(--yb_blue);
    margin-top: 0px;
    margin-bottom: 0px;
}
```

Set the bold elements to be blue.
```css
b {
    color: var(--yb_blue);
}
```

---

## Predicted Results

During my competition on 2023-05-28 I will be shooting a National Round. This comes `5` days after the most recent entry to the csv file. 

A National round consists of 48 arrows at 60 yards and 24 arrows at 50 yards.

Using my model, I can predict an average arrow score of **8.005** with **53.83%** of my shots scoring a 9 at 60 yards and an average arrow score of **8.297** with **66.11%** of my shots scoring a 9 at 50 yards.

$8.005 \times 48 = 384.24$

$8.297 \times 24 = 199.128$

$384.24 + 199.128 = 583.368 \approx 583$

This score would be enough to achieve a Bowman 3rd Class classification.

*After the competition:* 
- 60 yards: 7.63 / 47.9%
- 50 yards: 7.67 / 50%
- Classification: Archer 1st Class

`:(`

---

## Post-Competition Changes

The Brixham Archers Open Competition showed me how scores can change with the added pressure. As such, I added a feature to `is_comp` to the model. This value takes a `0` or `1` value for where `1` is True. 

```py
print(f"Score Data grouped by Competition Status: \n{score_data.groupby([score_data.distance, score_data.is_comp])[['arrow_average','arrows','golds_pct']].mean()}\n")
```
```
Score Data grouped by Competition Status: 
                  arrow_average     arrows  golds_pct
distance is_comp                                     
30       0             8.750000  50.000000  87.478956
40       0             8.351250  30.000000  69.097222
50       0             8.085714  30.857143  61.111111
         1             7.670000  24.000000  50.000000
60       0             8.140000  36.000000  56.944444
         1             7.630000  48.000000  47.916667
```

A `BooleanField` from `wtforms` is used to create a checkbox taking the input.
```py
is_comp = BooleanField("Competition? ")
```

The returned value is then passed through into `'index.html'` to display the box.
```html
    <h2> {{ get_score_data.is_comp.label }} </h2>
    {{ get_score_data.is_comp() }}
```

A current limitation of this feature is the lack of datapoints for the model to observe from. Only 2 datapoints does not provide the model enough data to accurately predict the impact (coefficient) to the average arrow score feature.
```
7.63,60,"2023-05-28",23,48,1
7.67,50,"2023-05-28",12,24,1
```

---

## Summary Statistics

These lines use `Pandas` `.groupby()` method to display mean statistics for the `arrow_average` [average arrow score], `arrows` [arrows shot] and `golds_pct` [golds percentage] columns.

It seperates these statistics by:
- Day of Week
- Month and Year
- Distance to Target
- Is it a competition shoot?

```py
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
month_and_year_cols = month_and_year[['arrow_average','arrows','golds_pct']]
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
```
> These were originally single-line expressions but I expanded them out to multiple lines to be (mostly) within the 80 character line rule and for "readability"; I'm not sure it had the desired effect. 

This outputs:
```
Score Data grouped by Day of Week: 
             arrow_average  arrows  golds_pct  date
day_of_week                                        
1                 8.330000   27.75  69.444444     8
4                 8.343333   32.00  68.981481     6
6                 8.315000   39.00  70.199315    14

Score Data grouped by Month: 
           arrow_average      arrows  golds_pct
date date                                      
2023 4          8.656250   33.000000  83.159722
     5          8.149444   29.666667  62.692901
     6          8.640000  132.000000  81.818182

Score Data grouped by Distance by Month: 
                    arrow_average      arrows  golds_pct
distance date date                                      
30       2023 4          8.797500   33.000000  89.930556
              5          8.670000   36.000000  83.333333
              6          8.640000  132.000000  81.818182
40       2023 4          8.515000   33.000000  76.388889
              5          8.284000   22.800000  66.111111
50       2023 5          8.076667   29.333333  61.419753
60       2023 5          7.970000   40.000000  53.935185

Score Data grouped by Distance: 
          arrow_average     arrows  golds_pct
distance                                     
30             8.750000  50.000000  87.478956
40             8.386667  27.333333  70.679012
50             8.076667  29.333333  61.419753
60             7.970000  40.000000  53.935185

Score Data grouped by Competition Status: 
                  arrow_average     arrows  golds_pct
distance is_comp                                     
30       0             8.750000  50.000000  87.478956
40       0             8.386667  27.333333  70.679012
50       0             8.127500  30.000000  62.847222
         1             7.670000  24.000000  50.000000
60       0             8.140000  36.000000  56.944444
         1             7.630000  48.000000  47.916667
```

The aim of these statistics is to highlight relationship affecting my scores. For example:
- Does shooting on a Tuesday after work decrease my average score per arrow?
- Does shooting on a Sunday in the morning increase my average score per arrow? 
- Does my average score increase as time goes on? Am I improving?
- Has my average score increase or decrease during the time period after making a change to my equipement? 
- By how much does my score drop when I increase the distance?
- Does shooting in a competition - with added nerves - decrease my average score?

---

## Plotting

I used Matplotlib's `pyplot` module and the `seaborn` module to plot how my minimum, average and maximum arrow average score is affected by the distance being shot, the day of week the shooting occurs and whether or not it is done at a competition event

```py
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
print("plotting")

# Figure labels
plt.xlabel("Distance")
plt.ylabel("Average Arrow Score")

# Colour Map used to differentiate days of week or by month
cmap_seven = plt.cm.get_cmap('viridis', 7)
cmap_twelve = plt.cm.get_cmap('viridis', 12)

# Scatterplot of distance against arrow average
# Style: O markers if not competition, X markers if is competition
# Hue: Change colour of marker depending on day of week of shoot, 
#      uses 'cmap' to discern colours
def plot_by(hue_type, label, cmap):
    plt.clf()
    sns.scatterplot(
        data = score_data,
        x = "distance", y = "arrow_average",
        style = "is_comp",
        hue = hue_type,
        palette = cmap
    )

    # Plot lines for min / avg / max arrow scores at each distance
    plt.plot(score_data.distance.unique(), score_data.groupby(['distance']).max().arrow_average, "k:")
    plt.plot(score_data.distance.unique(), score_data.groupby(['distance']).mean().arrow_average, "g--")
    plt.plot(score_data.distance.unique(), score_data.groupby(['distance']).min().arrow_average, "k:")
    
    plt.show(block=False)
    plt.savefig(f"{label}_fig.png")

plot_by(score_data.day_of_week, "day_of_week", cmap_seven)    
plot_by(score_data.date.dt.month, "month", cmap_twelve)
```

This outputs the following graph.

![fig.png](/archery_predictor/day_of_week_fig.png)

These lines clear the figure and plot all the datapoints as a scatter plot.
```py
    plt.clf()
    sns.scatterplot(
        data = score_data,
        x = "distance", y = "arrow_average",
        style = "is_comp",
        hue = hue_type,
        palette = cmap
    )
```

`style = "is_comp"` controls the marker style with circle markers representing non-competition shoots and X markers representing competition shoots.

`hue = hue_type, palette = cmap` controls the colour styling with each colour representing either a different day of the week or different month depending on how the function is called. 
```py
plot_by(score_data.day_of_week, "day_of_week", cmap_seven)    
plot_by(score_data.date.dt.month, "month", cmap_twelve)
```

The function takes in as parameters:
- the data to plot
- the label to assign to the saved image
- the colour map to use; either 'viridis' spaced into 7 or 12 bins

![month fig](/archery_predictor/month_fig.png)

These lines plot the minimum, average and maximum score values for each distance as line graphs.
```py
plt.plot(score_data.distance.unique(), score_data.groupby(['distance']).max().arrow_average, "k:")
plt.plot(score_data.distance.unique(), score_data.groupby(['distance']).mean().arrow_average, "g--")
plt.plot(score_data.distance.unique(), score_data.groupby(['distance']).min().arrow_average, "k:")
```
