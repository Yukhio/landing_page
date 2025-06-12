from flask import Flask, render_template
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

@app.route('/')
def home():
    hoy = date.today()
    fecha_nacimiento = datetime.strptime("1999-06-12", "%Y-%m-%d").date()
    inicio_trabajo = datetime.strptime("2024-12-02", "%Y-%m-%d").date()

    # Edad
    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    fecha_formateada = fecha_nacimiento.strftime("%d/%m/%Y")

    # Tiempo trabajando
    def calcular_tiempo_trabajando(inicio, fin):
        diferencia = relativedelta(fin, inicio)
        partes = []
        if diferencia.years:
            partes.append(f"{diferencia.years} año{'s' if diferencia.years > 1 else ''}")
        if diferencia.months:
            partes.append(f"{diferencia.months} mes{'es' if diferencia.months > 1 else ''}")
        if diferencia.days and not diferencia.years:
            partes.append(f"{diferencia.days} día{'s' if diferencia.days > 1 else ''}")
        return ", ".join(partes) if partes else "Hoy"

    # Tiempo para cumpleaños
    def calcular_tiempo_proximo_cumple(fecha_nac, hoy):
        proximo = fecha_nac.replace(year=hoy.year)
        if proximo < hoy:
            proximo = proximo.replace(year=hoy.year + 1)
        delta = relativedelta(proximo, hoy)
        if delta.years == 0 and delta.months == 0 and delta.days == 0:
            return "¡Feliz cumpleaños!"
        partes = []
        if delta.months:
            partes.append(f"{delta.months} mes{'es' if delta.months > 1 else ''}")
        if delta.days:
            partes.append(f"{delta.days} día{'s' if delta.days > 1 else ''}")
        return f"Faltan {', '.join(partes)} para tu próximo cumpleaños"

    es_cumple = (fecha_nacimiento.day == hoy.day and fecha_nacimiento.month == hoy.month)

    person = {
        "nombre": "Enrique Yukhio Juárez Preciado",
        "foto": "img/perfil.jpeg",
        "puesto": "Desarrollador Full Stack",
        "ubicacion": "Colima, Colima, México",
        "url": "https://www.linkedin.com/in/enrique-yukhio-ju%C3%A1rez-preciado-953b5b21a/",
        "email": "yukhio.000@gmail.com",
        "telefono": "+52 3121184818",
        "fecha_nacimiento": fecha_formateada,
        "edad": edad,
        "inicio_trabajo": inicio_trabajo.strftime("%d/%m/%Y"),
        "tiempo_trabajando": calcular_tiempo_trabajando(inicio_trabajo, hoy),
        "tiempo_para_cumple": calcular_tiempo_proximo_cumple(fecha_nacimiento, hoy),
        "es_cumpleanios": es_cumple
    }

    return render_template("index.html", person=person)

if __name__ == '__main__':
    app.run(debug=True)
