from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# HTML Template (Embedded)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BIN Checker Tool v1</title>
    <style>
        body { font-family: 'Arial', sans-serif; text-align: center; background: #1c1c1c; color: white; margin: 0; padding: 20px; }
        h2 { font-size: 32px; margin-bottom: 10px; }
        p { font-size: 18px; color: #bbb; }
        form { margin: 20px auto; max-width: 500px; background: #292929; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(255, 255, 255, 0.1); }
        textarea { width: 100%; height: 120px; font-size: 18px; padding: 10px; border-radius: 5px; border: none; background: #444; color: white; resize: none; }
        button { background: #ff4c4c; color: white; border: none; padding: 12px 20px; font-size: 18px; border-radius: 5px; cursor: pointer; transition: 0.3s; }
        button:hover { background: #e63939; }
        .result-box { max-width: 600px; margin: 20px auto; padding: 20px; background: #292929; border-radius: 8px; box-shadow: 0 0 10px rgba(255, 255, 255, 0.1); text-align: left; }
        .bin-result { padding: 12px; border-bottom: 1px solid #444; }
        .bin-result:last-child { border-bottom: none; }
    </style>
</head>
<body>
    <h2>BIN Checker Tool v1</h2>
    <p>Enter  BINs </p>
    
    <form method="post">
        <textarea name="bins" placeholder=" BINs here"></textarea><br>
        <button type="submit">Check BINs</button>
    </form>

    {% if results %}
    <div class="result-box">
        <h3>Results:</h3>
        {% for result in results %}
            <div class="bin-result">
                <strong>BIN:</strong> {{ result['bin'] }} <br>
                <strong>Bank:</strong> {{ result['bank'] }} <br>
                <strong>Country:</strong> {{ result['country'] }} ({{ result['emoji'] }}) <br>
                <strong>Type:</strong> {{ result['type'] }} | <strong>Scheme:</strong> {{ result['scheme'] }} <br>
            </div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
"""

def check_bin(bin_number):
    """Function to check BIN details using binlist API"""
    try:
        response = requests.get(f'https://lookup.binlist.net/{bin_number}')
        data = response.json()
        
        result = {
            'bin': bin_number,
            'bank': data.get('bank', {}).get('name', 'Unknown'),
            'country': data.get('country', {}).get('name', 'Unknown'),
            'emoji': data.get('country', {}).get('emoji', '🌍'),
            'scheme': data.get('scheme', 'Unknown'),
            'type': data.get('type', 'Unknown')
        }
        print(result)  # Debugging: Check if API returns valid data
        return result
    except Exception as e:
        print(f"Error fetching BIN {bin_number}: {e}")
        return None

@app.route("/BIN", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        bins_input = request.form.get("bins", "").splitlines()
        for bin_number in bins_input:
            bin_number = bin_number.strip()
            if bin_number:
                result = check_bin(bin_number)
                if result:
                    results.append(result)

    return render_template_string(HTML_TEMPLATE, results=results)

if __name__ == "__main__":
    app.run(debug=True)
