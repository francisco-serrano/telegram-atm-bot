import pandas as pd
import numpy as np
import sqlite3
import logging
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

db_file = os.getenv('DB_DIR', '/app/database/cajeros.db')
csv_file = os.getenv('CSV_DIR', '/app/data/cajeros-automaticos.csv')
table_name = os.getenv('TABLE_NAME', 'cajeros')
max_extractions = 999.9  # we need to force df.to_sql to create table with REAL datatype for the last column

logger.info('attempting to connect to database')

connection = sqlite3.connect(db_file, check_same_thread=False)

logger.info('connection to database successful')

df = pd.read_csv(csv_file)
df['prob_disponibilidad'] = np.repeat(max_extractions, len(df))

logger.info('atm csv successfully read')

df.to_sql(table_name, connection, if_exists='replace')

logger.info('dataframe dumped to database')

connection.commit()
connection.close()

logger.info('database setup successful')
