from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Crea la carpeta si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USUARIOS_FILE = "usuarios.json"

def cargar_usuarios():
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for u in data.values():
                u.setdefault("tareas", [])
            return data
    return {}


def guardar_usuarios(data):
    with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

MENSAJES_FILE = "mensajes.json"

def cargar_mensajes():
    if os.path.exists(MENSAJES_FILE):
        with open(MENSAJES_FILE, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            return json.loads(contenido) if contenido else []
    return []

def guardar_mensajes(mensajes):
    with open(MENSAJES_FILE, "w", encoding="utf-8") as f:
        json.dump(mensajes, f, indent=2, ensure_ascii=False)


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
                "foto": foto_url,
                "tareas": []  # Inicializa las tareas vacías
            }

            guardar_usuarios(usuarios)
            session['mensaje_login'] = '¡Usuario registrado con éxito! Ahora puedes iniciar sesión.'
            return redirect(url_for('login'))
    return render_template('registro.html', mensaje=mensaje)


@app.route('/perfil', methods=['GET', 'POST'])
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

    diferencia = relativedelta(hoy, inicio_trabajo)
    partes = []
    if diferencia.years:
        partes.append(f"{diferencia.years} año{'s' if diferencia.years > 1 else ''}")
    if diferencia.months:
        partes.append(f"{diferencia.months} mes{'es' if diferencia.months > 1 else ''}")
    if diferencia.days and not diferencia.years:
        partes.append(f"{diferencia.days} día{'s' if diferencia.days > 1 else ''}")
    tiempo_trabajando = ", ".join(partes) if partes else "Hoy"

    proximo = fecha_nacimiento.replace(year=hoy.year)
    if proximo < hoy:
        proximo = proximo.replace(year=hoy.year + 1)
    delta = relativedelta(proximo, hoy)
    es_cumple = hoy.month == fecha_nacimiento.month and hoy.day == fecha_nacimiento.day
    tiempo_para_cumple = (
        "¡Feliz cumpleaños!" if es_cumple
        else f"Faltan {delta.months} meses, {delta.days} días para tu próximo cumpleaños"
    )

    if request.method == 'POST':
        titulo = request.form.get("titulo")
        subtitulos = request.form.getlist("subtitulo[]")
        descripciones = request.form.getlist("descripcion[]")

        if titulo and subtitulos and descripciones and len(subtitulos) == len(descripciones):
            subtareas = [
                {"titulo": st, "descripcion": desc}
                for st, desc in zip(subtitulos, descripciones)
            ]
            usuarios[username].setdefault("tareas", []).append({
                "titulo": titulo,
                "subtareas": subtareas,
                "completada": False
            })
            guardar_usuarios(usuarios)
            return redirect(url_for("perfil"))


    return render_template("perfil.html", person={
        **user,
        "edad": edad,
        "fecha_nacimiento": fecha_formateada,
        "inicio_trabajo": inicio_formateado,
        "tiempo_trabajando": tiempo_trabajando,
        "tiempo_para_cumple": tiempo_para_cumple,
        "es_cumpleanios": es_cumple
    }, mostrar_bienvenida=mostrar_bienvenida, tareas=user.get("tareas", []), usuarios=usuarios)

@app.route('/ver-perfil/<username>', methods=['GET', 'POST'])
def ver_perfil(username):
    if username not in usuarios:
        return redirect(url_for('lista_perfiles'))

    user = usuarios[username]

    hoy = date.today()
    fecha_nacimiento = datetime.strptime(user['fecha_nacimiento'], "%Y-%m-%d").date()
    inicio_trabajo = datetime.strptime(user['inicio_trabajo'], "%Y-%m-%d").date()

    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    fecha_formateada = fecha_nacimiento.strftime("%d/%m/%Y")
    inicio_formateado = inicio_trabajo.strftime("%d/%m/%Y")

    diferencia = relativedelta(hoy, inicio_trabajo)
    partes = []
    if diferencia.years:
        partes.append(f"{diferencia.years} año{'s' if diferencia.years > 1 else ''}")
    if diferencia.months:
        partes.append(f"{diferencia.months} mes{'es' if diferencia.months > 1 else ''}")
    if diferencia.days and not diferencia.years:
        partes.append(f"{diferencia.days} día{'s' if diferencia.days > 1 else ''}")
    tiempo_trabajando = ", ".join(partes) if partes else "Hoy"

    proximo = fecha_nacimiento.replace(year=hoy.year)
    if proximo < hoy:
        proximo = proximo.replace(year=hoy.year + 1)
    delta = relativedelta(proximo, hoy)
    es_cumple = hoy.month == fecha_nacimiento.month and hoy.day == fecha_nacimiento.day
    tiempo_para_cumple = (
        "¡Feliz cumpleaños!" if es_cumple
        else f"Faltan {delta.months} meses, {delta.days} días para tu próximo cumpleaños"
    )

    return render_template("perfil.html", person={
        **user,
        "edad": edad,
        "fecha_nacimiento": fecha_formateada,
        "inicio_trabajo": inicio_formateado,
        "tiempo_trabajando": tiempo_trabajando,
        "tiempo_para_cumple": tiempo_para_cumple,
        "es_cumpleanios": es_cumple
    }, mostrar_bienvenida=False, tareas=user.get("tareas", []))

@app.route('/cambiar-perfil/<username>')
def cambiar_perfil(username):
    if username in usuarios:
        session['username'] = username
        session['show_welcome'] = True
    return redirect(url_for('perfil'))


@app.route('/eliminar-tarea', methods=['POST'])
def eliminar_tarea():
    username = session.get('username')
    if not username or username not in usuarios:
        return redirect(url_for('login'))

    indice = int(request.form.get('indice', -1))
    if 0 <= indice < len(usuarios[username].get("tareas", [])):
        usuarios[username]["tareas"].pop(indice)
        guardar_usuarios(usuarios)

    return redirect(url_for('perfil'))


@app.route('/completar-tarea', methods=['POST'])
def completar_tarea():
    username = session.get('username')
    if not username or username not in usuarios:
        return redirect(url_for('login'))

    indice = int(request.form.get('indice', -1))
    if 0 <= indice < len(usuarios[username].get("tareas", [])):
        usuarios[username]["tareas"][indice]['completada'] = True
        guardar_usuarios(usuarios)

    return redirect(url_for('perfil'))


@app.route('/mensajes', methods=['GET'])
def obtener_mensajes():
    emisor = session.get('username')
    receptor = request.args.get('con')
    if not emisor or not receptor:
        return jsonify([])

    mensajes = cargar_mensajes()
    conversacion = [
        m for m in mensajes
        if (m['emisor'] == emisor and m['receptor'] == receptor) or
           (m['emisor'] == receptor and m['receptor'] == emisor)
    ]
    return jsonify(conversacion)

@app.route('/enviar-mensaje', methods=['POST'])
def enviar_mensaje():
    emisor = session.get('username')
    receptor = request.form.get('receptor')
    contenido = request.form.get('contenido')

    if emisor and receptor and contenido:
        mensajes = cargar_mensajes()
        mensajes.append({
            "emisor": emisor,
            "receptor": receptor,
            "contenido": contenido,
            "timestamp": datetime.utcnow().isoformat()
        })
        guardar_mensajes(mensajes)
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 400


@app.route('/perfiles')
def lista_perfiles():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('perfiles.html', usuarios=usuarios)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

if __name__ == '__main__':
    app.run(debug=True)
