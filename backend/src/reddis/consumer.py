import os
import pika
import psycopg2
import redis
from datetime import datetime, timedelta
import json
from typing import List, Dict

# Fetch environment variables
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_QUEUE = 'active_users'

POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Connect to PostgreSQL
def get_postgres_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

# Connect to Redis
def get_redis_connection():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Fetch files data for a user from PostgreSQL
def fetch_files_data(user_id: int) -> List[Dict]:
    if not isinstance(user_id, int):
        raise ValueError("user_id must be an integer")

    query: str = """
        SELECT file_id, name, size, created
        FROM files
        WHERE user_id = %s
    """
    try:
        with get_postgres_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                rows = cursor.fetchall()
                columns = [col_desc[0] for col_desc in cursor.description]
                result = [dict(zip(columns, row)) for row in rows]  # Convert to readable format
        return result
    except Exception as e:
        # Log or handle the error appropriately
        print(f"Error fetching files data: {e}")
        raise

# Store data in Redis
def store_in_redis(user_id, data):
    r = get_redis_connection()
    key = f"user_files:{user_id}"
    r.set(key, json.dumps(data))

# Clear data older than 30 minutes from Redis
def clear_old_data_from_redis():
    r = get_redis_connection()
    threshold = datetime.now() - timedelta(minutes=30)
    for key in r.keys("user_files:*"):
        data = json.loads(r.get(key))
        updated_data = [item for item in data if datetime.fromisoformat(item['created']) > threshold]
        if updated_data:
            r.set(key, json.dumps(updated_data))
        else:
            r.delete(key)

# RabbitMQ callback function
def callback(ch, method, properties, body):
    user_id = body.decode('utf-8')
    print(f"Processing user: {user_id}")

    # Fetch files data for the user
    files_data = fetch_files_data(user_id)
    formatted_data = [
        {
            "file_id": str(row[0]),
            "name": row[1],
            "size": row[2],
            "created": row[3].isoformat()
        }
        for row in files_data
    ]

    # Store data in Redis
    store_in_redis(user_id, formatted_data)
    print(f"Stored data in Redis for user: {user_id}")

    # Clear old data from Redis
    clear_old_data_from_redis()
    print("Cleared old data from Redis")

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Main function
def main():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

    # Set up the consumer
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)

    print("Waiting for messages. To exit, press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    main()