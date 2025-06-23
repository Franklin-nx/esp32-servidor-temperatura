from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# Conexión con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Registro_Temperaturas").sheet1

# Función de alerta por correo (opcional)
def enviar_alerta(temp):
    if float(temp) > 90:
        msg = EmailMessage()
        msg.set_content(f"⚠️ Alerta: Temperatura crítica registrada: {temp} °C")
        msg["Subject"] = "Alerta de Temperatura ESP32"
        msg["From"] = "TUCORREO@gmail.com"
        msg["To"] = "DESTINATARIO@gmail.com"

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("TUCORREO@gmail.com", "CONTRASEÑA_APP")
            smtp.send_message(msg)

@app.route("/registro", methods=["POST"])
def registro():
    data = request.get_json()
    temperatura = data["temperatura"]
    estado_rele = "ON" if data["estado_rele"] == 1 else "OFF"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.append_row([fecha, temperatura, estado_rele])
    enviar_alerta(temperatura)
    return jsonify({"status": "ok"}), 200

@app.route("/estado_actual", methods=["GET"])
def estado_actual():
    ultima_fila = sheet.get_all_values()[-1]
    return jsonify({
        "fecha": ultima_fila[0],
        "temperatura": ultima_fila[1],
        "rele": ultima_fila[2]
    })

if __name__ == "__main__":
    app.run(debug=True)