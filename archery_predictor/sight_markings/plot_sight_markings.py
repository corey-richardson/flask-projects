import pandas as pd
import numpy as np
from sklearn import linear_model
from matplotlib import pyplot as plt

distance_to_predict = 80
is_metres = 0

def convert_to_yards(distance, is_metres):
    if not is_metres: # if yards, no conversion necessary
        return distance
    return distance * 1.09361

distance_to_predict = convert_to_yards(distance_to_predict, is_metres)

scope = pd.read_csv(f"../static/sight_marks.csv", header = 0)
distances = scope["distance"]
sight_markings = scope["sight_marking"]

ranging = list(range(0,110,10))

distances = np.reshape(distances, (-1, 1))
sight_markings = np.reshape(sight_markings, (-1, 1))
ranging = np.reshape(ranging, (-1, 1))
distance_to_predict = np.reshape(distance_to_predict, (-1, 1))

model = linear_model.LinearRegression()
model.fit(distances, sight_markings)
predicted_sight_markings = model.predict(ranging)
distance_predicted = model.predict(distance_to_predict)

plt.scatter(distances, sight_markings, color='k', marker='x')
plt.plot(ranging, predicted_sight_markings)
plt.axhline(distance_predicted, color="k", linestyle="dashed")

plt.title(f"{distance_predicted[0][0]:.2f} @ {distance_to_predict[0][0]:.2f} yards")
plt.savefig("sight_markings.png")