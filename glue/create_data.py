"""
This script does the following:
1. Connects to the PostgreSQL database and reads a sample of at most MAX_NUM_ARTICLES articles.
2. Creates NUM_USERS random users with random names and emails.
3. For each user, creates between MIN_ARTICLE_HITS and MAX_ARTICLE_HITS random article hits (page views) with random
    timestamps between 0 and MAX_PAST_DAYS days in the past.
4. Creates a CSV file with as many rows as PERC_USERS of the users generated, with the following columns:
    - email: The email of the user.
    - country: The country of the user (randomly generated).
"""

import csv
import random
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

import faker
import psycopg2
from tqdm import tqdm

MAX_NUM_ARTICLES = 1000  # Maximum number of articles to fetch from the database
NUM_USERS = 100  # Number of random users to create
MIN_ARTICLE_HITS = 10  # Minimum number of article hits per user
MAX_ARTICLE_HITS = 100  # Maximum number of article hits per user
MAX_PAST_DAYS = 30  # Maximum number of days in the past for random timestamps
PERC_USERS = 0.9  # Percentage of users to include in the CSV file


def main(pg_host: str, pg_port: int, pg_db: str, pg_user: str, pg_password: str, csv_file_path: str):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(host=pg_host, port=pg_port, database=pg_db, user=pg_user, password=pg_password)
    cursor = conn.cursor()

    # Read a sample of at most 1000 articles
    print("Fetching articles from the database...")
    cursor.execute(f"SELECT id FROM form_feeds ORDER BY RANDOM() LIMIT {MAX_NUM_ARTICLES:d}")  # Avoid SQL injection
    articles: List[Tuple[int]] = cursor.fetchall()
    article_ids = [article[0] for article in articles]

    print(f"Fetched {len(article_ids)} articles from the database.")
    fake = faker.Faker()  # This is used to generate random names and emails

    if len(article_ids) == 0:
        # If you get this error, you might have skipped some part of the setup,
        # because the web page should have created some articles when it started.
        # Please check that you've followed the instructions in the README file.
        raise ValueError("No articles found in the database.")

    # Create 100 random users with random names, emails and countries
    users: List[Tuple[int, str]] = []
    for _ in tqdm(range(NUM_USERS), desc="Generating random users", unit="user", leave=False, ncols=100):
        name = fake.name()
        email = fake.email()
        preview = random.choice([True, False])
        cursor.execute(
            "INSERT INTO form_leads (name, email, preview) VALUES (%s, %s, %s) RETURNING id, email",
            (name, email, preview),
        )
        user_id, email = cursor.fetchone()
        users.append((user_id, email))

    conn.commit()
    print(f"Created {len(users)} random users.")

    # Create random article hits for each user
    total_hits = 0
    for user_id, _ in tqdm(users, desc="Generating random article hits", unit="user", leave=False, ncols=100):
        num_hits = random.randint(MIN_ARTICLE_HITS, MAX_ARTICLE_HITS)
        for _ in range(num_hits):
            article_id = random.choice(article_ids)
            seconds_ago = random.randint(0, MAX_PAST_DAYS * 24 * 60 * 60)
            timestamp = datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
            cursor.execute(
                "INSERT INTO form_articlehits (lead_id, feed_id, timestamp) VALUES (%s, %s, %s)",
                (user_id, article_id, timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")),
            )
            total_hits += 1
    conn.commit()
    print(f"Created {total_hits} random article hits for {len(users)} users.")

    # Create a CSV file with the random user data

    with open(csv_file_path, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["email", "country"])

        # Select a sample of the created users
        num_users_to_include = int(len(users) * PERC_USERS)
        users_to_include = random.sample(users, num_users_to_include)
        for _, email in tqdm(users_to_include, desc="Generating countries in CSV", unit="user", leave=False, ncols=100):
            country = fake.country()
            writer.writerow({"email": email, "country": country})

    print(f"Created CSV file with random user data at {csv_file_path}.")

    # Close the database connection
    cursor.close()
    conn.close()


if __name__ == "__main__":
    import argparse

    import dotenv

    parser = argparse.ArgumentParser(description="Create random user data.")
    parser.add_argument("dotenv_path", type=str, help="Path to the .env file")
    args = parser.parse_args()

    env_vars = dotenv.dotenv_values(args.dotenv_path)
    pg_user = env_vars.get("POSTGRES_USER", "postgres")
    pg_port = int(env_vars.get("POSTGRES_PORT", 5432))
    pg_db = env_vars.get("POSTGRES_DB", "postgres")
    if not "POSTGRES_HOST" in env_vars:
        raise ValueError("POSTGRES_HOST is not set in the provided .env file")
    pg_host = env_vars.get("POSTGRES_HOST")
    if not "POSTGRES_PASSWORD" in env_vars:
        raise ValueError("POSTGRES_PASSWORD is not set in the provided .env file")
    pg_password = env_vars.get("POSTGRES_PASSWORD")

    main(
        pg_host=pg_host,
        pg_port=pg_port,
        pg_db=pg_db,
        pg_user=pg_user,
        pg_password=pg_password,
        csv_file_path="user_data.csv",
    )
