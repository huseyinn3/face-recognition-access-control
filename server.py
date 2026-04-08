from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import cv2
import base64
import json
import os
from datetime import datetime
from collections import Counter

app = Flask(__name__)

FACES_FILE = "known_faces.json"
HISTORY_FILE = "recognition_history.json"
STATS_FILE = "person_stats.json"

known_faces = {}
recognition_history = []
person_stats = {}

def load_data():
    global known_faces, recognition_history, person_stats
    
    if os.path.exists(FACES_FILE):
        try:
            with open(FACES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for name, encoding_list in data.items():
                    known_faces[name] = np.array(encoding_list)
        except:
            known_faces = {}
    
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                recognition_history = json.load(f)
        except:
            recognition_history = []
    
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                person_stats = json.load(f)
        except:
            person_stats = {}
    
    for name in known_faces.keys():
        if name not in person_stats:
            person_stats[name] = {
                "total_recognitions": 0,
                "last_seen": "Henuz tanimlanmadi",
                "first_registered": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

load_data()

def save_faces():
    data = {}
    for name, encoding in known_faces.items():
        data[name] = encoding.tolist()
    with open(FACES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_history():
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(recognition_history[-100:], f, ensure_ascii=False, indent=2)

def save_stats():
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(person_stats, f, ensure_ascii=False, indent=2)

@app.route('/')
def home():
    recent = recognition_history[-10:][::-1]
    name_counts = Counter([h['name'] for h in recognition_history if h['name'] != 'Bilinmeyen'])
    
    # Kisi kartlari
    person_cards = ""
    for name in known_faces.keys():
        stats = person_stats.get(name, {})
        person_cards += f"""
        <div class="person-card">
            <div class="person-name">👤 {name}</div>
            <div class="person-detail">
                <span>Tanima:</span>
                <span class="badge badge-success">{stats.get('total_recognitions', 0)} kez</span>
            </div>
            <div class="person-detail">
                <span>Son Gorulme:</span>
                <span>{stats.get('last_seen', 'Yok')}</span>
            </div>
            <button class="btn btn-danger" onclick="deleteFace('{name}')">Sil</button>
        </div>
        """
    
    # Gecmis tablosu
    history_rows = ""
    for h in recent:
        badge_class = 'badge-success' if h['name'] != 'Bilinmeyen' else 'badge-warning'
        history_rows += f"""
        <tr>
            <td><strong>{h['name']}</strong></td>
            <td><span class="badge {badge_class}">{h.get('confidence', 'N/A')}</span></td>
            <td>{h['timestamp']}</td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: Arial;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            h1 {{ text-align: center; margin: 30px 0; font-size: 2.5em; }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .stat-card {{
                background: rgba(255,255,255,0.2);
                padding: 25px;
                border-radius: 15px;
                text-align: center;
            }}
            .stat-number {{
                font-size: 3em;
                font-weight: bold;
                color: #FFD700;
            }}
            .stat-label {{ margin-top: 10px; }}
            .section {{
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 30px;
                margin: 20px 0;
            }}
            .section h2 {{
                margin-bottom: 20px;
                border-bottom: 2px solid rgba(255,255,255,0.3);
                padding-bottom: 15px;
            }}
            .person-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
            }}
            .person-card {{
                background: rgba(255,255,255,0.2);
                padding: 20px;
                border-radius: 15px;
            }}
            .person-name {{
                font-size: 1.5em;
                font-weight: bold;
                margin-bottom: 15px;
                color: #FFD700;
            }}
            .person-detail {{
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }}
            .btn {{
                background: white;
                color: #667eea;
                border: none;
                padding: 10px 20px;
                border-radius: 20px;
                cursor: pointer;
                font-weight: bold;
                margin-top: 10px;
            }}
            .btn-danger {{
                background: #ff4757;
                color: white;
            }}
            .history-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            .history-table th, .history-table td {{
                padding: 15px;
                text-align: left;
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }}
            .history-table th {{
                background: rgba(255,255,255,0.2);
            }}
            .chart-container {{
                background: white;
                padding: 20px;
                border-radius: 15px;
            }}
            .badge {{
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
            }}
            .badge-success {{ background: #2ed573; }}
            .badge-warning {{ background: #ffa502; }}
            .empty {{ text-align: center; padding: 40px; opacity: 0.7; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Gelismis Dashboard</h1>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(known_faces)}</div>
                    <div class="stat-label">Kayitli Kisi</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(recognition_history)}</div>
                    <div class="stat-label">Toplam Tanima</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([h for h in recognition_history if h['name'] != 'Bilinmeyen'])}</div>
                    <div class="stat-label">Basarili</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📈 Grafik</h2>
                <div class="chart-container">
                    <canvas id="chart"></canvas>
                </div>
            </div>
            
            <div class="section">
                <h2>👥 Kayitli Kisiler</h2>
                {"<div class='empty'>Kayitli kisi yok</div>" if len(known_faces) == 0 else f'<div class="person-grid">{person_cards}</div>'}
            </div>
            
            <div class="section">
                <h2>📜 Son 10 Tanima</h2>
                {"<div class='empty'>Gecmis yok</div>" if len(recent) == 0 else f'''
                <table class="history-table">
                    <tr><th>Isim</th><th>Guven</th><th>Zaman</th></tr>
                    {history_rows}
                </table>
                '''}
            </div>
        </div>
        
        <script>
            new Chart(document.getElementById('chart'), {{
                type: 'bar',
                data: {{
                    labels: {list(name_counts.keys())},
                    datasets: [{{
                        label: 'Tanima Sayisi',
                        data: {list(name_counts.values())},
                        backgroundColor: ['rgba(255,99,132,0.7)', 'rgba(54,162,235,0.7)', 'rgba(255,206,86,0.7)']
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{ y: {{ beginAtZero: true }} }}
                }}
            }});
            
            function deleteFace(name) {{
                if(confirm(name + ' silinsin mi?')) {{
                    fetch('/delete', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{name: name}})
                    }}).then(() => location.reload());
                }}
            }}
        </script>
    </body>
    </html>
    """
    return html

@app.route('/register', methods=['POST'])
def register_face():
    try:
        data = request.json
        name = data.get('name', 'Kullanici')
        image_data = base64.b64decode(data['image'])
        
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        encodings = face_recognition.face_encodings(rgb)
        
        if len(encodings) > 0:
            known_faces[name] = encodings[0]
            save_faces()
            
            person_stats[name] = {
                "total_recognitions": 0,
                "last_seen": "Henuz tanimlanmadi",
                "first_registered": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_stats()
            
            return jsonify({"success": True, "message": f"{name} kaydedildi!", "total_faces": len(known_faces)})
        else:
            return jsonify({"success": False, "message": "Yuz bulunamadi!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/recognize', methods=['POST'])
def recognize_face():
    try:
        data = request.json
        image_data = base64.b64decode(data['image'])
        
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb)
        face_encodings = face_recognition.face_encodings(rgb, face_locations)
        
        results = []
        
        for encoding in face_encodings:
            name = "Bilinmeyen"
            confidence = 0
            
            if len(known_faces) > 0:
                known_names = list(known_faces.keys())
                known_encodings = list(known_faces.values())
                
                matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.6)
                face_distances = face_recognition.face_distance(known_encodings, encoding)
                
                if True in matches:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_names[best_match_index]
                        confidence = (1 - face_distances[best_match_index]) * 100
                        
                        person_stats[name]['total_recognitions'] += 1
                        person_stats[name]['last_seen'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        save_stats()
            
            recognition_history.append({
                "name": name,
                "confidence": f"{confidence:.1f}%",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_history()
            
            results.append({"name": name, "confidence": f"{confidence:.1f}%"})
        
        if len(results) == 0:
            return jsonify({"success": False, "message": "Yuz bulunamadi!"})
        
        return jsonify({"success": True, "faces": results, "count": len(results)})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/list', methods=['GET'])
def list_faces():
    return jsonify({"success": True, "faces": list(known_faces.keys()), "count": len(known_faces)})

@app.route('/delete', methods=['POST'])
def delete_face():
    try:
        data = request.json
        name = data.get('name')
        
        if name in known_faces:
            del known_faces[name]
            save_faces()
            
            if name in person_stats:
                del person_stats[name]
                save_stats()
            
            return jsonify({"success": True, "message": f"{name} silindi!"})
        else:
            return jsonify({"success": False, "message": "Bulunamadi!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == '__main__':
    print("="*60)
    print("DASHBOARD BASLATILUYOR...")
    print(f"Kayitli: {len(known_faces)}")
    print("http://localhost:5000")
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=True)