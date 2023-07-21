import xmltodict
import requests
import pandas as pd

from airflow.decorators import dag, task
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.providers.sqlite.hooks.sqlite import SqliteHook

import pendulum


PODCAST_URL = "https://www.marketplace.org/feed/podcast/marketplace/"

@dag(
    dag_id='podcast_summary',
    schedule_interval="@daily",
    start_date=pendulum.datetime(2023, 7, 20),
    catchup=False,
    
)
def podcast_summary():

    create_database = SqliteOperator(
        task_id="create_table_sqlite",
        sql=r"""
        CREATE TABLE IF NOT EXISTS episodes (
            link TEXT PRIMARY KEY,
            title TEXT,
            filename TEXT,
            published TEXT,
            description TEXT
        )
        """,
        sqlite_conn_id="podcasts"
    )

    @task()
    def get_episodes():
        data = requests.get(PODCAST_URL)
        feed = xmltodict.parse(data.text)
        episodes = feed["rss"]["channel"]["item"] # contém cada podcast individual do scraping

        print(f"Found {len(episodes)} episodes.")

        return episodes

    podcast_episodes = get_episodes()

    @task()
    def load_episodes(episodes):
        hook = SqliteHook(sqlite_conn_id="podcasts")
        stored = hook.get_pandas_df("SELECT * FROM episodes;")
        new_episodes = []

        for episode in episodes:
            if episode["link"] not in stored["link"].values:
                filename = f"{episode['link'].split('/')[-1]}.mp3"
                new_episodes.append([episode["link"], episode["title"], episode["pubDate"], episode["description"], filename])
        hook.insert_rows(table="episodes", rows=new_episodes, target_fields=["link", "title", "published", "description", "filename"])

    store_data = load_episodes(podcast_episodes)
    
    create_database >> podcast_episodes >> store_data

summary = podcast_summary()