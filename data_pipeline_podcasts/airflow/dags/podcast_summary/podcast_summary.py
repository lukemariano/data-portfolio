import xmltodict
import requests

from airflow.decorators import dag, task
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
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
        """
    )

    @task()
    def get_episodes():
        data = requests.get(PODCAST_URL)
        feed = xmltodict.parse(data.text)
        episodes = feed["rss"]["channel"]["item"] # contém cada podcast individual do scraping

        print(f"Found {len(episodes)} episodes.")

        return episodes

    podcast_episodes = get_episodes()
    
    create_database >> podcast_episodes

summary = podcast_summary()