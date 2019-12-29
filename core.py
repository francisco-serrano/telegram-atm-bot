import pandas as pd
import numpy as np

from geopy import distance

my_location = (-37.340859, -59.122895)

df = pd.read_csv('cajeros-automaticos.csv')
df['mi_long'] = np.repeat(my_location[0], len(df))
df['mi_lat'] = np.repeat(my_location[1], len(df))

df['distance'] = df[['long', 'lat', 'mi_long', 'mi_lat']].apply(
    lambda row: distance.distance((row['long'], row['lat']), (row['mi_long'], row['mi_lat'])).meters, axis=1
)

df = df.sort_values(by='distance', ascending=True)

print(df.head(3))