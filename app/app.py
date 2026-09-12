from flask import Flask, jsonify
import os
import psycopg2

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "devopsdb")
DB_USER = os.getenv("POSTGRES_USER", "devopsuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "devopspass")


@app.route("/")
def home():
    return """
    <html>
        <head>
            <title>DevOps Trainee Assignment</title>
        </head>
        <body>
            <h1>IT Infrastructure & DevOps Trainee</h1>
            <p>Application is running successfully.</p>
            <p>Backend: Flask</p>
            <p>Database: PostgreSQL</p>
            <p>Reverse Proxy: Nginx</p>
        </body>
    </html>
    """


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "Flask",
        "database": "PostgreSQL"
    })


@app.route("/db-test")
def db_test():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.close()

        return jsonify({
            "database_connection": "successful"
        })

    except Exception as e:
        return jsonify({
            "database_connection": "failed",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
