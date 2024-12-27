import jwt, datetime, os
from flask import Flask, request, redirect, url_for
from flask_mysqldb import MySQL
import bcrypt
import uuid

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))


@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    # Retrieve form data
    first_name = data.get('first_name')
    middle_name = data.get('middle_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')  # Password entered by user
    country_code = data.get('country_code')
    phone_number = data.get('phone_number')
    birth_date = data.get('birth_date')
    gender = data.get('gender')
    last_ip_address = data.get('last_ip_address')

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Create a new user ID (UUID)
    user_id = str(uuid.uuid4())

    # Create the insert query
    query = """
        INSERT INTO users (user_id, password_hash, first_name, middle_name, last_name, email, 
                           country_code, phone_number, birth_date, gender, last_ip_address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        user_id,
        hashed_password.decode('utf-8'),
        first_name,
        middle_name,
        last_name,
        email,
        country_code,
        phone_number,
        birth_date,
        gender,
        last_ip_address
    )

    # Execute the query
    cursor = mysql.connection.cursor()
    try:
        cursor.execute(query, values)
        mysql.connection.commit()
        cursor.close()
        # After successful registration, redirect to the login page
        return redirect(url_for('login'))
    except Exception as e:
        cursor.close()
        return "invalid credentials", 401


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    # check db for username and password
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password_hash FROM user WHERE email=%s", (auth.username,)
    )

    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "invalid credentials", 401


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
    except:
        return "not authorized", 403

    return decoded, 200


def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
