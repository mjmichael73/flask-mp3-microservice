import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL
import logging

server = Flask(__name__)
mysql = MySQL(server)

# Config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST", "localhost")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER", "root")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "toor")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB", "auth_service_db")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT", 3306))
server.config["JWT_SECRET"] = os.environ.get("JWT_SECRET", "jwt_secret")


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401
    # Check DB for username and password
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )
    if res <= 0:
        return "invalid credentials", 401
    user_row = cur.fetchone()
    email = user_row[0]
    password = user_row[1]
    if auth.username != email or auth.password != password:
        return "invalid credentials", 401
    return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]
    if not encoded_jwt:
        return "missing authorization", 401
    encoded_jwt = encoded_jwt.spit(" ")[1]
    try:
        decoded = jwt.decode(
            encoded_jwt,
            os.environ.get("JWT_SECRET", "jwt_secret"),
            algorithm="HS256"
        )
    except Exception as e:
        return "not authorized", 401
    return decoded, 200

@server.route("/health", methods=["GET"])
def health():
    return "Up&Running", 200

def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz
        },
        secret,
        algorithm="HS256"
    )


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
