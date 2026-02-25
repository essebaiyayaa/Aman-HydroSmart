# ============================================================
#  AQUAFARM AI — Flask App complet
#  Lance avec : python app.py
# ============================================================

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt
import pandas as pd
import random
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "aquafarm_secret_2024"

# ─── SQLite ───────────────────────────────────────────────
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///aquafarm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ─── Gemini API ───────────────────────────────────────────
API_KEY = "AIzaSyDAb2_MBQZkoUVqs-29MALwzHqmLzHouNY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ─── CSV — tes vraies colonnes ────────────────────────────
# ph, Hardness, Solids, Chloramines, Sulfate,
# Conductivity, Organic_carbon, Trihalomethanes, Turbidity, Potability
try:
    df = pd.read_csv("water.csv")
    df = df.fillna(df.mean(numeric_only=True))  # remplace cellules vides par moyenne
    df = df.reset_index(drop=True)
    print(f"✅ CSV chargé : {len(df)} lignes")
    print(f"   Colonnes   : {list(df.columns)}")
except Exception as e:
    df = None
    print(f"⚠️ water.csv introuvable : {e}")

# Compteur global — avance d'une ligne à chaque appel /api/sensors
csv_index = [0]

# ══════════════════════════════════════════════════════════
#  MODELE USER
# ══════════════════════════════════════════════════════════
class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100))
    email    = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

with app.app_context():
    db.create_all()

# ══════════════════════════════════════════════════════════
#  HELPER — Lire ligne suivante du CSV
# ══════════════════════════════════════════════════════════
def get_sensor():
    if df is not None:
        i   = csv_index[0] % len(df)
        row = df.iloc[i]
        csv_index[0] += 1
        return {
            "ph":              round(float(row.get("ph",              6.5)),  2),
            "hardness":        round(float(row.get("Hardness",        200)),  2),
            "solids":          round(float(row.get("Solids",          20000)),0),
            "chloramines":     round(float(row.get("Chloramines",     7.0)),  2),
            "sulfate":         round(float(row.get("Sulfate",         350)),  2),
            "conductivity":    round(float(row.get("Conductivity",    450)),  2),
            "organic_carbon":  round(float(row.get("Organic_carbon",  14)),   2),
            "trihalomethanes": round(float(row.get("Trihalomethanes", 70)),   2),
            "turbidity":       round(float(row.get("Turbidity",       3.5)),  2),
            "potability":      int(row.get("Potability", 0)),
            "solar":           round(random.uniform(2.0, 6.0), 2),
            "battery":         round(random.uniform(40,  95),  1),
            "water_saved":     int(random.uniform(200, 400)),
            "row_number":      i + 1,
        }
    else:
        return {
            "ph": 6.5, "hardness": 200, "solids": 20000,
            "chloramines": 7.0, "sulfate": 350, "conductivity": 450,
            "organic_carbon": 14, "trihalomethanes": 70, "turbidity": 3.5,
            "potability": 0, "solar": 4.0, "battery": 75, "water_saved": 300,
            "row_number": 0,
        }

def get_alerts(data):
    alerts = []
    if data["ph"] < 5.5 or data["ph"] > 7.5:
        alerts.append(f"⚠️ pH anormal : {data['ph']} — Ajuster maintenant")
    if data["turbidity"] > 4.0:
        alerts.append(f"⚠️ Turbidité élevée : {data['turbidity']} NTU")
    if data["chloramines"] > 8.0:
        alerts.append(f"⚠️ Chloramines élevées : {data['chloramines']} mg/L")
    if data["battery"] < 20:
        alerts.append(f"🔋 Batterie faible : {data['battery']}%")
    if data["potability"] == 0:
        alerts.append("🚱 Eau NON potable selon analyse")
    return alerts

# ══════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════
@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email    = request.form["email"]
        password = request.form["password"]
        user     = User.query.filter_by(email=email).first()
        if user and bcrypt.verify(password, user.password):
            session["user"] = user.email
            session["name"] = user.name
            return redirect(url_for("dashboard"))
        error = "Email ou mot de passe incorrect"
    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name     = request.form["name"]
        email    = request.form["email"]
        password = request.form["password"]
        if User.query.filter_by(email=email).first():
            error = "Email déjà utilisé"
        else:
            user = User(name=name, email=email, password=bcrypt.hash(password.encode('utf-8')[:72]))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("register.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session["name"])

# ══════════════════════════════════════════════════════════
#  API JSON
# ══════════════════════════════════════════════════════════
@app.route("/api/sensors")
def api_sensors():
    data   = get_sensor()
    alerts = get_alerts(data)
    return jsonify({"data": data, "alerts": alerts})

@app.route("/api/report")
def api_report():
    data  = get_sensor()
    score = 100
    issues = []
    if data["ph"] < 5.5 or data["ph"] > 7.5:
        score -= 25; issues.append("pH hors norme")
    if data["turbidity"] > 4.0:
        score -= 20; issues.append("turbidité élevée")
    if data["chloramines"] > 8.0:
        score -= 20; issues.append("chloramines élevées")
    if data["potability"] == 0:
        score -= 15; issues.append("eau non potable")
    status = "excellente 🟢" if score >= 80 else "acceptable 🟡" if score >= 50 else "critique 🔴"
    detail = f"Problèmes : {', '.join(issues)}." if issues else "Tous les paramètres sont normaux ✅"
    return jsonify({
        "score":   score,
        "summary": f"Qualité eau : {status} ({score}/100). {detail} Eau économisée : {data['water_saved']} L."
    })

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data    = get_sensor()
    alerts  = get_alerts(data)
    message = request.json.get("message", "Analyse mon eau")
    potable = "OUI ✅" if data["potability"] == 1 else "NON ❌"
    prompt = f"""
Tu es AquaBot, expert qualité d'eau pour agriculture hydroponique.
Réponds en français. Court et pratique. Maximum 3 points. Utilise des emojis.

=== DONNÉES RÉELLES CSV (ligne {data['row_number']}) ===
• pH                : {data['ph']}         (optimal : 5.5–7.0)
• Dureté            : {data['hardness']} mg/L
• Solides dissous   : {data['solids']} ppm
• Chloramines       : {data['chloramines']} mg/L  (limite : 8)
• Sulfates          : {data['sulfate']} mg/L
• Conductivité      : {data['conductivity']} μS/cm
• Carbone organique : {data['organic_carbon']} mg/L
• Trihalométhanes   : {data['trihalomethanes']} μg/L
• Turbidité         : {data['turbidity']} NTU  (limite : 4)
• Eau potable       : {potable}
• Batterie          : {data['battery']}%
• Eau économisée    : {data['water_saved']} L/jour
• Alertes           : {', '.join(alerts) if alerts else 'Aucune'}

=== QUESTION ===
{message}

Dis clairement si l'eau est utilisable pour l'agriculture.
Si non, dis exactement QUOI corriger et COMMENT.
"""
    response = model.generate_content(prompt)
    return jsonify({"response": response.text})

# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(debug=True, port=5000)