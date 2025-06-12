from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # Puedes reemplazar estos valores por lo que necesites
    person = {
        "name": "Enrique Yukhio Juárez Preciado",
        "photo": "img/perfil.jpeg",
        "job_title": "Desarrollador Full Stack",
        "location": "Colima, Colima, México",
        "contact_url": "https://www.linkedin.com/in/enrique-yukhio-ju%C3%A1rez-preciado-953b5b21a/"
    }
    return render_template("index.html", person=person)

if __name__ == '__main__':
    app.run(debug=True)
