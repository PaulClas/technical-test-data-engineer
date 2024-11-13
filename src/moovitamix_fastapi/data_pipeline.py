import requests
import schedule
import time
from datetime import datetime
import os
import logging
import argparse
import threading
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, JSON, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from concurrent.futures import ThreadPoolExecutor, as_completed
from prometheus_client import start_http_server, Summary, Counter, Gauge
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("data_pipeline.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
ERROR_COUNT = Counter('pipeline_errors_total', 'Total number of errors in the pipeline')
DATA_PROCESSED = Counter('data_processed_total', 'Total amount of data processed')
CPU_USAGE = Gauge('cpu_usage', 'CPU usage of the pipeline')
MEMORY_USAGE = Gauge('memory_usage', 'Memory usage of the pipeline')

# Remarque : Pour des raisons de sécurité, API_BASE_URL et DATABASE_URL doivent être stockés dans un fichier .env et non codés en claire dans le script.
# Comme il s'agit d'un simple test à exécuter aussi facilement que possible, ces variables sont codées en clair ci-dessous.
# Cela est particulièrement important dans les environnements de production pour éviter d'exposer des informations sensibles.
API_BASE_URL = "http://127.0.0.1:8000"
DATABASE_URL = "postgresql://username:password@localhost/recommendation_db?sslmode=disable"

# Define the metadata and tables at the module level
metadata = MetaData()

tracks_table = Table('tracks', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(255), nullable=False),
    Column('artist', String(255), nullable=False),
    Column('songwriters', String(255)),
    Column('duration', String(50)),
    Column('genres', String(255)),
    Column('album', String(255)),
    Column('created_at', TIMESTAMP, nullable=False),
    Column('updated_at', TIMESTAMP, nullable=False)
)

users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('first_name', String(255), nullable=False),
    Column('last_name', String(255), nullable=False),
    Column('email', String(255), unique=True, nullable=False),
    Column('gender', String(50)),
    Column('favorite_genres', String(255)),
    Column('created_at', TIMESTAMP, nullable=False),
    Column('updated_at', TIMESTAMP, nullable=False)
)

listen_history_table = Table('listen_history', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('items', JSON),
    Column('created_at', TIMESTAMP, nullable=False),
    Column('updated_at', TIMESTAMP, nullable=False)
)

# Function to create the database if it doesn't exist
def create_database():
    from psycopg2 import connect
    conn = connect("postgresql://username:password@localhost/postgres")
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'recommendation_db'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute('CREATE DATABASE recommendation_db')
        logger.info("Database 'recommendation_db' created successfully.")
    else:
        logger.info("Database 'recommendation_db' already exists.")
    cursor.close()
    conn.close()

# Function to create tables if they don't exist
def create_tables(engine):
    metadata.create_all(engine)
    logger.info("Tables created successfully.")

# Set up the database connection
create_database()
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()

def test_db_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("Database connection successful: %s", result.fetchone())
    except SQLAlchemyError as e:
        logger.error("Database connection failed: %s", e)
        raise

@REQUEST_TIME.time()
def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch data from {endpoint}: {e}")
        ERROR_COUNT.inc()
        raise

@REQUEST_TIME.time()
def save_data_to_db(data, table):
    start_time = time.time()
    try:
        stmt = insert(table).values(data['items'])
        stmt = stmt.on_conflict_do_nothing() 
        session.execute(stmt)
        session.commit()
        duration = time.time() - start_time
        logger.info(f"Saved {len(data['items'])} records to {table.name} in {duration:.2f} seconds")
        DATA_PROCESSED.inc(len(data['items']))
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Failed to save data to {table.name}: {e}")
        ERROR_COUNT.inc()
        raise

def retrieve_and_save_data():
    logger.info("Starting data retrieval")

    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(fetch_data, endpoint): endpoint for endpoint in ["users", "tracks", "listen_history"]
            }
            results = {}
            for future in as_completed(futures):
                endpoint = futures[future]
                try:
                    data = future.result()
                    results[endpoint] = data
                except Exception as e:
                    logger.error(f"An error occurred while processing {endpoint}: {e}")
                    ERROR_COUNT.inc()

        # Save users first to ensure foreign key constraints are met
        if "users" in results:
            save_data_to_db(results["users"], users_table)

        # Save tracks
        if "tracks" in results:
            save_data_to_db(results["tracks"], tracks_table)

        # Save listen history
        if "listen_history" in results:
            save_data_to_db(results["listen_history"], listen_history_table)

        logger.info("Data retrieval completed successfully")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        ERROR_COUNT.inc()

def manual_trigger_listener():
    while True:
        command = input("Entrez 'run' pour déclencher manuellement le pipeline de données : ")
        if command.strip().lower() == 'run':
            retrieve_and_save_data()

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Data Pipeline")
    parser.add_argument('--run-once', action='store_true', help="Exécuter le pipeline une fois immédiatement")
    args = parser.parse_args()

    # Start Prometheus metrics server
    start_http_server(8080)

    # Test the database connection
    test_db_connection()

    if args.run_once:
        # Run the pipeline once immediately
        retrieve_and_save_data()
    else:
        # Schedule the task to run daily at midnight
        schedule.every().day.at("00:00").do(retrieve_and_save_data)

        # Start a thread to listen for manual trigger commands
        listener_thread = threading.Thread(target=manual_trigger_listener)
        listener_thread.daemon = True
        listener_thread.start()

        # Run the scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    main()