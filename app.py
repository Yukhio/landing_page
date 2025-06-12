from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'clave-secreta-segura'  # necesaria para usar sesiones

UPLOAD_FOLDER = 'static/img/perfiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crea la carpeta si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USUARIOS_FILE = "usuarios.json"

def cargar_usuarios():
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_usuarios(data):
    with open(USUARIOS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# Usuarios de ejemplo
usuarios = cargar_usuarios()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = session.pop('mensaje_login', '')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = usuarios.get(username)

        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('perfil'))
        else:
            mensaje = 'Usuario o contraseña incorrectos.'
    return render_template('login.html', mensaje=mensaje)


@app.route('/perfil')
def perfil():
    username = session.get('username')
    if not username or username not in usuarios:
        return redirect(url_for('login'))

    user = usuarios[username]
    mostrar_bienvenida = session.pop('show_welcome', False)

    hoy = date.today()
    fecha_nacimiento = datetime.strptime(user['fecha_nacimiento'], "%Y-%m-%d").date()
    inicio_trabajo = datetime.strptime(user['inicio_trabajo'], "%Y-%m-%d").date()

    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    fecha_formateada = fecha_nacimiento.strftime("%d/%m/%Y")
    inicio_formateado = inicio_trabajo.strftime("%d/%m/%Y")

    # Tiempo trabajado
    diferencia = relativedelta(hoy, inicio_trabajo)
    partes = []
    if diferencia.years:
        partes.append(f"{diferencia.years} año{'s' if diferencia.years > 1 else ''}")
    if diferencia.months:
        partes.append(f"{diferencia.months} mes{'es' if diferencia.months > 1 else ''}")
    if diferencia.days and not diferencia.years:
        partes.append(f"{diferencia.days} día{'s' if diferencia.days > 1 else ''}")
    tiempo_trabajando = ", ".join(partes) if partes else "Hoy"

    # Próximo cumpleaños
    proximo = fecha_nacimiento.replace(year=hoy.year)
    if proximo < hoy:
        proximo = proximo.replace(year=hoy.year + 1)
    delta = relativedelta(proximo, hoy)
    es_cumple = hoy.month == fecha_nacimiento.month and hoy.day == fecha_nacimiento.day
    if es_cumple:
        tiempo_para_cumple = "¡Feliz cumpleaños!"
    else:
        partes_cumple = []
        if delta.months:
            partes_cumple.append(f"{delta.months} mes{'es' if delta.months > 1 else ''}")
        if delta.days:
            partes_cumple.append(f"{delta.days} día{'s' if delta.days > 1 else ''}")
        tiempo_para_cumple = f"Faltan {', '.join(partes_cumple)} para tu próximo cumpleaños"

    return render_template("perfil.html", person={
        **user,
        "edad": edad,
        "fecha_nacimiento": fecha_formateada,
        "inicio_trabajo": inicio_formateado,
        "tiempo_trabajando": tiempo_trabajando,
        "tiempo_para_cumple": tiempo_para_cumple,
        "es_cumpleanios": es_cumple
    }, mostrar_bienvenida=mostrar_bienvenida)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    mensaje = ''
    if request.method == 'POST':
        username = request.form['username']
        if username in usuarios:
            mensaje = 'El nombre de usuario ya está registrado.'
        else:
            # Verifica archivo
            foto = request.files['foto']
            if foto and allowed_file(foto.filename):
                filename = secure_filename(f"{username}_{foto.filename}")
                foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                foto.save(foto_path)
                foto_url = f"img/perfiles/{filename}"
            else:
                mensaje = 'Formato de imagen no permitido.'
                return render_template('registro.html', mensaje=mensaje)

            usuarios[username] = {
                "password": request.form['password'],
                "nombre": request.form['nombre'],
                "puesto": request.form['puesto'],
                "ubicacion": request.form['ubicacion'],
                "email": request.form['email'],
                "telefono": request.form['telefono'],
                "fecha_nacimiento": request.form['fecha_nacimiento'],
                "inicio_trabajo": request.form['inicio_trabajo'],
                "foto": foto_url
            }
            session['mensaje_login'] = '¡Usuario registrado con éxito! Ahora puedes iniciar sesión.'
            return redirect(url_for('login'))
    return render_template('registro.html', mensaje=mensaje)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

if __name__ == '__main__':
    app.run(debug=True)
