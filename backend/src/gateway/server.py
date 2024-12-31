import os, pika, json
from flask import Flask, request, send_file, send_from_directory
from auth import validate
from auth_svc import access
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import psycopg2

#TODO: save the file in structured format uid/folder/file
#TODO: fetch from the reddis server
#TODO: method to create new user
server = Flask(__name__)

# Folder where files will be uploaded
UPLOAD_FOLDER = '/var/lib/upload/'
server.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set a limit for uploaded files (e.g., 2GB)
server.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip'}

def fetch_data_from_postgres(query: str):
    # Fetch database credentials from environment variables
    global cursor, connection
    db_config = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', '5432')  # Default PostgreSQL port
    }

    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchone()
        return rows

    except psycopg2.Error as e:
        print(f"An error occurred while connecting to the database: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def publish_to_queue(filename,quee_name):
    try:
        # Establish a connection to RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Declare a queue
        channel.queue_declare(queue=quee_name, durable=True)

        # Publish the filename to the queue
        channel.basic_publish(
            exchange='',
            routing_key=quee_name,
            body=filename,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make the message persistent
            )
        )

        print(f" [x] Sent {filename} to RabbitMQ queue")

        # Close the connection
        connection.close()

    except Exception as e:
        print(f"Error publishing to RabbitMQ: {e}")

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err


@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400

        if 'file' not in request.files:
            return "No file part", 400
    file = request.files['file']

    # If no file is selected
    if file.filename == '':
        return "No selected file", 400

    # Check if the file is allowed
    if file and allowed_file(file.filename):
        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)

        # Save the file to the upload folder
        file_path = os.path.join(server.config['UPLOAD_FOLDER'], filename)

        # Make sure the upload folder exists, create if not
        if not os.path.exists(server.config['UPLOAD_FOLDER']):
            os.makedirs(server.config['UPLOAD_FOLDER'])

        # Save the file
        file.save(file_path)

        active_user = request.headers.get("active_user")

        # After saving, push the filename to RabbitMQ
        publish_to_queue(filename, "encryptor")
        publish_to_queue(active_user, "active_users")

        return "sucess!", 200
    else:
        return "not authorized", 401


@server.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # Check if the file exists in the upload folder
        file_path = os.path.join(server.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return "File not found", 404

        # Return the file for download
        return send_from_directory(server.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        return "Error downloading the file: {e}", 500


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
