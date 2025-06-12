from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.secret_key = 'clave-secreta-segura'  # necesaria para usar sesiones

def inject_now():
    return {'now': datetime.utcnow}

# Usuarios de ejemplo
usuarios = {
    "enrique": {
        "password": "123456",
        "nombre": "Enrique Yukhio Juárez Preciado",
        "foto": "img/perfil.jpeg",
        "puesto": "Desarrollador Full Stack",
        "ubicacion": "Colima, Colima, México",
        "email": "yukhio.000@gmail.com",
        "telefono": "+52 3121184818",
        "fecha_nacimiento": "1999-12-08",
        "inicio_trabajo": "2024-12-02"
    }
}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ''
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
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
