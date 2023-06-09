import pandas as pd
import numpy as np
from sklearn import linear_model
from matplotlib import pyplot as plt

# Set the distance you need sight markings for.
# If the distances entered is metres (for metric rounds), set 'is_metres'
# to True or 1.
distance_to_predict = 80
is_metres = 0

# Function to convert metres to yards
def convert_to_yards(distance):
    return distance * 1.09361

if is_metres:
    distance_to_predict = convert_to_yards(distance_to_predict)

# Read data from csv
scope = pd.read_csv(f"sight_markings/sight_marks.csv", header = 0)
distances = scope["distance"]
sight_markings = scope["sight_marking"]

# Generate a list of values 10, 20, ..., 100.
# This is used as input to the model prediction as well as the x-axis in
# the resultant plot.
ranging = list(range(0,110,10))

# Reshape into a 'inferred' by 1 array
distances = np.reshape(distances, (-1, 1))
sight_markings = np.reshape(sight_markings, (-1, 1))
ranging = np.reshape(ranging, (-1, 1))
distance_to_predict = np.reshape(distance_to_predict, (-1, 1))

# Create and fit the model
# Predict values to plot, and user specified distance
model = linear_model.LinearRegression()
model.fit(distances, sight_markings)
predicted_sight_markings = model.predict(ranging)
distance_predicted = model.predict(distance_to_predict)

# Plot
plt.scatter(distances, sight_markings, color='k', marker='x')
plt.plot(ranging, predicted_sight_markings)
plt.axhline(distance_predicted, color="r", linestyle="dashed")
plt.axhline(0, color="k", linestyle=":", alpha=0.5)
plt.axhline(6, color="k", linestyle=":", alpha=0.5)

print(f"At 0yds: {model.intercept_[0]:.2f}")
print(f"Delta per 10yds: {model.coef_[0][0] * 10:.2f}")
print(f"At {distance_to_predict[0][0]:.2f}yds: {distance_predicted[0][0]:.2f}")

plt.title(f"{distance_predicted[0][0]:.2f} @ {distance_to_predict[0][0]:.2f} yards")
plt.savefig("sight_markings/sight_markings.png")