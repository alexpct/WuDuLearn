from flask import Flask, request, redirect, render_template, session, jsonify
from flask_mysqldb import MySQL
from pylti.flask import lti
import docker
import os
import logging
from dotenv import load_dotenv
from flask_socketio import SocketIO

# Load environment variables from .env file
load_dotenv()

# Configure logging system
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
socketio = SocketIO(app)
# Load secret keys and database configuration from environment variables
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')

app.config['LTI_KEY'] = os.getenv('LTI_KEY', 'default-lti-key')
app.config['LTI_SECRET'] = os.getenv('LTI_SECRET', 'default-lti-secret')

app.config['PYLTI_CONFIG'] = {
    'consumers': {
        app.config['LTI_KEY']: {
            'secret': app.config['LTI_SECRET']
        }
    }
}

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'user')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'password')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'database')
mysql = MySQL(app)

TEST_MODE = True

def error_handler(exception=None):
    if TEST_MODE:
        session['lti_data'] = {
            'user_id': '1337',
            'lis_person_name_full': 'Test User',
            'custom_module': 'terminal',
            'lis_person_name_given': "Test"
        }
        return redirect("/compute")
    else:
        return "Authentication error"

@app.route("/lti", methods=["GET", "POST"])
@lti(request='initial', error=error_handler, app=app)
def lti_handler():
    session['lti_data'] = {key: value for key, value in request.form.items()}
    return redirect("/compute")

def manage_docker_container(user_id, module_name):
    client = docker.from_env()

    allowed_modules = os.getenv('ALLOWED_MODULES', '').split(',')
    if module_name is None or module_name not in allowed_modules:
        app.logger.error("Invalid or missing module name")
        return

    container_name = f"{user_id}_{module_name}".lower()

    try:
        # Versuche, den Container zu erhalten
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        # Wenn der Container nicht existiert, erstelle ihn im interaktiven Modus
        try:
            container = client.containers.run(module_name, name=container_name, detach=True, stdin_open=True, tty=True)
        except docker.errors.DockerException as e:
            app.logger.error(f"Error creating Docker container: {e}")
            return

    # Starte den Container, wenn er nicht läuft
    if container.status != 'running':
        try:
            container.start()
        except docker.errors.DockerException as e:
            app.logger.error(f"Error starting Docker container: {e}")


@app.route("/terminal", methods=["GET", "POST"])
def terminal():
    lti_data = session.get('lti_data', {})
    return render_template("terminal.html", lti_data=lti_data)

@app.route("/get-lti-data", methods=["GET"])
def get_lti_data():
    lti_data = session.get('lti_data', {})
    return jsonify(lti_data)


@app.route("/compute", methods=["GET", "POST"])
def compute():
    app.logger.info("Compute Route aufgerufen")

    lti_data = session.get('lti_data', {})
    user_id = lti_data.get('user_id')
    app.logger.info(f"Empfangene user_id: {user_id}")

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT * FROM User WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            app.logger.info(f"Benutzer gefunden: {user}")
            cursor.execute("UPDATE User SET LastLogin = NOW() WHERE id = %s", (user_id,))
        else:
            app.logger.info("Neuer Benutzer wird hinzugefügt")
            cursor.execute("INSERT INTO User (id) VALUES (%s)", (user_id,))

        mysql.connection.commit()
    except Exception as e:
        app.logger.error(f"Database error: {e}")
        mysql.connection.rollback()
        return f"Ein Fehler ist aufgetreten: {e}"
    finally:
        cursor.close()

    custom_module = lti_data.get('custom_module')
    manage_docker_container(user_id, custom_module)
    return redirect("/terminal")

# Additional Flask routes...

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
