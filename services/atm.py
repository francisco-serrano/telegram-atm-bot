from utils.logger import logger
import numpy as np
import matplotlib.pyplot as plt
import requests
import shutil
import time
import os
import glob
import pandas as pd
from geopy import distance
from functools import reduce
from database import database


def current_milli_time():
    return int(round(time.time() * 1000))


class ATMService:
    csv_file = os.getenv('CSV_DIR', './data/cajeros-automaticos.csv')
    db_file = os.getenv('DB_DIR', './database/cajeros.db')

    df = pd.read_csv(csv_file)
    df = df[df['localidad'] == 'CABA']

    db = database.CajerosDatabase(db_file)

    token = 'none'
    token_time = 0

    def __init__(self):
        self.verify_token_expiration()

        for f in glob.glob('*.png'):
            os.remove(f)

    def obtain_atms(self, lat, long, vendor):
        custom_df = ATMService.df.copy()
        custom_df['mi_lat'] = np.repeat(lat, len(custom_df))
        custom_df['mi_long'] = np.repeat(long, len(custom_df))

        custom_df['distance'] = custom_df[['long', 'lat', 'mi_long', 'mi_lat']].apply(
            lambda row: distance.distance((row['long'], row['lat']), (row['mi_long'], row['mi_lat'])).meters,
            axis=1
        )

        custom_df = custom_df[custom_df['distance'].lt(500)]
        custom_df = custom_df.sort_values(by='distance', ascending=True)
        custom_df = custom_df[custom_df['red'] == vendor.upper()].head(3)

        logger.info('amount of ATMs found: {}'.format(len(custom_df)))

        if len(custom_df) == 0:
            return None, None

        atms = custom_df[['banco', 'ubicacion']].values
        atms = ATMService.db.get_and_extract(atms)
        atms = reduce(lambda a, b: '{}\n{}'.format(a, b), atms)

        atm_coords = custom_df[['lat', 'long']].append({'lat': lat, 'long': long}, ignore_index=True)

        return atms, atm_coords

    def obtain_image(self, coords):
        filename = self.obtain_map(coords)

        logger.info('final image temporarily generated in {}'.format(filename))

        return filename

    def obtain_map(self, coords):
        min_lat = coords['lat'].min() - 0.001
        max_lat = coords['lat'].max() + 0.001
        min_long = coords['long'].min() - 0.001
        max_long = coords['long'].max() + 0.001

        url = 'https://render.openstreetmap.org/cgi-bin/export?bbox={},{},{},{}&scale=2600&format=png'.format(
            min_long, min_lat, max_long, max_lat
        )

        self.verify_token_expiration()

        response = requests.request('GET', url, cookies={'_osm_totp_token': ATMService.token}, stream=True)

        logger.info('status code from OpenStreetMap {} using token {}'.format(response.status_code, ATMService.token))

        filename = 'file_{}.png'.format(current_milli_time())

        file = open(filename, 'wb')
        shutil.copyfileobj(response.raw, file)
        file.close()

        logger.info('raw file temporarily stored in {}'.format(filename))

        bbox = (min_long, max_long, min_lat, max_lat)

        image = plt.imread(filename)

        fig, ax = plt.subplots(dpi=1000)
        ax.scatter(coords['long'], coords['lat'], zorder=1, alpha=0.8, c='b', s=50)
        ax.imshow(image, zorder=0, extent=bbox, aspect='equal')

        plt.axis('off')

        new_filename = 'new_{}'.format(filename)

        ax.imshow(image, zorder=0, extent=bbox, aspect='equal')
        fig.savefig(new_filename, dpi=fig.dpi, bbox_inches='tight')

        return new_filename

    def verify_token_expiration(self):
        now = time.time()
        if now - ATMService.token_time >= 1800:
            response = requests.request('GET', 'https://www.openstreetmap.org/#map=4/-40.44/-63.59')
            ATMService.token = response.cookies.get('_osm_totp_token')
            ATMService.token_time = now
            logger.info('token obtained from OpenStreetMap {}'.format(ATMService.token))
