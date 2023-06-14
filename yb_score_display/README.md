# Yelverton Bowmen Score Display

---

Intended for use at community events, such as the annual Plympton Lamb Feast.

---

## User Guide

### Running the Flask Project

```
cd yb_score_display
```
```
source bin/activate
flask run
```

### Setting Up

The script will then ask for the event name in the console terminal.
```
Event Name:
```

Type the name of the event and press the <kbd>Enter</kbd> key to continue.
```
Event Name: Plympton Lamb Feast
 * Debugger is active!
 * Debugger PIN: XXX-XXX-XXX
127.0.0.1 - - [14/Jun/2023 14:29:11] "GET / HTTP/1.1" 200 -
...
```

### Add a Score

To add a new score, click on the 'Add a Score' button in the top navigation bar. This will bring up a form to be filled in.

Label | Field Type | Required
--- | --- | ---
Name | String Field | :heavy_check_mark:
Score | Integer Field | :heavy_check_mark:
Age Category | Dropdown Box | :heavy_check_mark:
Sex | Dropdown Box |  :heavy_check_mark:
Email | Email Validation Field | :x:
Phone Number | String Field | :x:

> `Sex` is a required field however there is an option to select 'Prefer not to say'. <br>
> Phone Number is a `StringField` rather than an `IntegerField` to avoid stripping the starting '0' at the start of UK style phone numbers.

![](/yb_score_display/README_assets/form.PNG)
![](/yb_score_display/README_assets/form_validation.PNG)

### Scoreboard

As new scores are added, the scoreboard updates, sorting itself from highest to lowest score acheived.

![](/yb_score_display/README_assets/scoreboard.PNG)

The scoreboard also measures the number of entries, as well as the average score.

### Final Results

At the *cessation* of activities, use the 'View Results' tab, found in the upper navigation bar to display the top **five** (or other as set by `N_WINNERS` in `app.py`) scores for each of the following categories:
- Overall
- Seniors
- Juniors
- Gents
- Ladies

![](/yb_score_display/README_assets/results.PNG)

### Clearing the Scores

To clear the scores, navigate to `static/scores.csv` and paste the following, overwriting and pre-existing data:
```
name,score,age_category,sex,email,phone_num

```
> NOTE: The empty new-line after the headers is REQUIRED.

I intentionally did not add functionality within the web application to avoid any accidental deletions during the event day.