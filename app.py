from flask import Flask, request, redirect, render_template_string, send_file
import qrcode
import qrcode.image.svg
import io
import json

app = Flask(__name__)

# Trwała baza danych w pliku JSON
DB_FILE = 'routes.json'

def load_routes():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "aw66025": "https://awtools.pl/manuals/aw66025.pdf"
        }

def save_routes(routes):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(routes, f, indent=4, ensure_ascii=False)

DYNAMIC_ROUTES = load_routes()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generator Kodów QR (Druk & Etykiety)</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 30px auto; padding: 0 20px; background: #f8f9fa; color: #333; }
        h1, h2 { color: #1a1a1a; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 25px; }
        label { font-weight: 600; display: block; margin-top: 15px; margin-bottom: 5px; }
        input, select, button { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        input:focus, select:focus { border-color: #0066cc; outline: none; }
        button { background: #0066cc; color: white; border: none; font-weight: bold; margin-top: 20px; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #0052a3; }
        .qr-result { text-align: center; margin-top: 25px; padding-top: 25px; border-top: 2px dashed #eee; }
        .qr-result svg { max-width: 220px; height: auto; border: 1px solid #ddd; padding: 10px; background: white; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; background: #28a745; }
        .badge-dynamic { background: #fd7e14; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #fafafa; font-size: 13px; text-transform: uppercase; color: #666; }
        code { background: #eef; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="card">
        <h1>📦 Generator Kodów QR na Opakowania</h1>
        <p style="color: #666;">Twórz bezpłatne statyczne i dynamiczne kody QR gotowe do druku (high error correction Level H).</p>
        
        <form method="POST" action="/generate">
            <label for="type">Typ kodu QR:</label>
            <select name="type" id="type">
                <option value="dynamic">Dynamiczny (Zalecany na pudełka - pozwala zmienić PDF bez przedruku)</option>
                <option value="static">Statyczny (Bezpośredni adres URL na stałe)</option>
            </select>

            <label for="url">Docelowy adres URL (np. link do pliku PDF / instrukcji):</label>
            <input type="url" name="url" id="url" placeholder="https://awtools.pl/manuals/instrukcja.pdf" required>

            <label for="alias">Identyfikator kodu dynamicznego (opcjonalnie, np. <code>aw66025</code>):</label>
            <input type="text" name="alias" id="alias" placeholder="zostaw puste dla automatycznego numeru">

            <button type="submit">Generuj Wektorowy QR (SVG)</button>
        </form>

        {% if qr_svg %}
        <div class="qr-result">
            <h3>Wygenerowany kod QR</h3>
            <div>{{ qr_svg | safe }}</div>
            <p style="margin-top: 15px;">
                <strong>Zakodowany adres w QR:</strong><br>
                <code>{{ encoded_url }}</code>
            </p>
            {% if target_url %}
            <p><strong>Aktualne przekierowanie docelowe:</strong><br><a href="{{ target_url }}" target="_blank">{{ target_url }}</a></p>
            {% endif %}
        </div>
        {% endif %}
    </div>

    <div class="card">
        <h2>Aktywne Przekierowania Dynamiczne</h2>
        {% if routes %}
        <table>
            <thead>
                <tr>
                    <th>Adres QR (z druku)</th>
                    <th>Docelowy PDF / URL</th>
                    <th>Akcja</th>
                </tr>
            </thead>
            <tbody>
                {% for code, target in routes.items() %}
                <tr>
                    <td><code>/qr/{{ code }}</code></td>
                    <td style="max-width: 300px; word-break: break-all;">{{ target }}</td>
                    <td><a href="/qr/{{ code }}" target="_blank">Testuj link</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p style="color: #888;">Brak zarejestrowanych kodów dynamicznych.</p>
        {% endif %}
    </div>
</body>
</html>
"""

def make_qr_svg(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    stream = io.BytesIO()
    img.save(stream)
    return stream.getvalue().decode('utf-8')

@app.route('/', methods=['GET'])
def index():
    routes = load_routes()
    return render_template_string(HTML_TEMPLATE, routes=routes)

@app.route('/generate', methods=['POST'])
def generate():
    routes = load_routes()
    qr_type = request.form.get('type')
    target_url = request.form.get('url').strip()
    alias = request.form.get('alias').strip()

    if qr_type == 'static':
        encoded_url = target_url
        target_info = None
    else:
        short_code = alias if alias else f"prod-{len(routes) + 1}"
        routes[short_code] = target_url
        save_routes(routes)
        
        host_url = request.host_url.rstrip('/')
        encoded_url = f"{host_url}/qr/{short_code}"
        target_info = target_url

    svg_code = make_qr_svg(encoded_url)
    return render_template_string(
        HTML_TEMPLATE, 
        qr_svg=svg_code, 
        encoded_url=encoded_url, 
        target_url=target_info, 
        routes=routes
    )

@app.route('/qr/<short_code>')
def redirect_short_code(short_code):
    routes = load_routes()
    target = routes.get(short_code)
    if target:
        return redirect(target, code=302)
    return "<h3>Błąd 404: Kod QR nie istnieje lub wygasł.</h3>", 404

if __name__ == '__main__':
    print("Serwer uruchomiony w sieci na http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
