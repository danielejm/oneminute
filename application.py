from flask import Flask, render_template, request, session
from flask_session import Session
import re
import os
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
ROLES = ['estudiante', 'profesor']

app = Flask(__name__)
#El nombre del usuario y la clave de la base de datos se leen del sistema operativo
dbUser = os.environ['dbUser']
dbPass = os.environ['dbPass']
# Debe escribir el link a su  cluster de MongoDB Atlas
client = pymongo.MongoClient(f"mongodb+srv://{dbUser}:{dbPass}@cluster0.twnzg.mongodb.net/oneminute?retryWrites=true&w=majority")
db = client.oneminute


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
    # Se debe validar que se hayan ingresado los datos necesarios. En caso de que haya un error se va construyendo un mensaje de error
        msgError = ""
        nuevoUsuario = {}
        print(request.form)
    #con este primer if se revisa si en el formulario viene el campo nombres.
        if "nombres" in request.form:
            nuevoUsuario["nombres"] = request.form.get("nombres").strip()
            if not nuevoUsuario["nombres"]:
                msgError += "Debe ingresar un nombre válido. "
        if "apellidos" in request.form:
            nuevoUsuario["apellidos"] = request.form.get("apellidos").strip()
            if not nuevoUsuario["apellidos"]:
                msgError += "Debe ingresar un apellido válido "
        if "correo" in request.form:
            nuevoUsuario["correo"] = request.form.get("correo").strip()
            if not nuevoUsuario["correo"]:
                msgError += "Debe ingresar un correo válido "
            elif not EMAIL_REGEX.match(nuevoUsuario["correo"]):
                msgError += "Debe ingresar un correo válido. "
        if "rol" in request.form:
            nuevoUsuario["roles"] = [request.form.get("rol").strip()]
            if nuevoUsuario["roles"][0] not in ROLES:
                msgError += "Debe ingresar un rol válido. "
            elif nuevoUsuario["roles"][0] == ROLES[1]:
                nuevoUsuario["roles"].append(ROLES[0])
        if "clave" in request.form:
            nuevoUsuario["clave"] = request.form.get("clave")
            if not nuevoUsuario["clave"]:
                msgError += "Debe ingresar una contraseña válida. "
            else:
                if "confClave" in request.form:
                    if nuevoUsuario["clave"] != request.form.get("confClave"):
                        msgError += "Las dos contraseñas deben coincidir. "
        if msgError != "":
            return render_template("register.html", msg=msgError)
        else:
            nuevoUsuario["clave"] = generate_password_hash(nuevoUsuario["clave"])
            try:
                result = db.usuarios.insert_one(nuevoUsuario)
            except pymongo.errors.DuplicateKeyError:
                msgError += "El correo ingresado no está disponible"
                return render_template("register.html", msg=msgError)
            return render_template("index.html", user = nuevoUsuario, result = result)
if __name__ == "__main__":
      app.run(host='0.0.0.0', port=5500)

