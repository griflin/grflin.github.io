from flask import Flask, render_template, jsonify, request, session
import os
from wifi_pentest import WifiPentestTool
from datetime import datetime
import yaml

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Load config
with open('config/default_config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

# Global tool instance
pentest_tool = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/init', methods=['POST'])
def initialize():
    global pentest_tool
    try:
        data = request.json
        interface = data.get('interface', CONFIG['interface']['default'])
        target_ssid = data.get('ssid', '')
        wordlist = data.get('wordlist', CONFIG['wordlists']['default_path'])
        
        pentest_tool = WifiPentestTool(
            interface=interface,
            target_ssid=target_ssid,
            wordlist_path=wordlist,
            output_dir='output'
        )
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/scan')
def scan_networks():
    if not pentest_tool:
        return jsonify({'status': 'error', 'message': 'Tool not initialized'})
    
    try:
        networks = pentest_tool.scan_wifi()
        return jsonify({
            'status': 'success',
            'networks': networks
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/attack', methods=['POST'])
def start_attack():
    if not pentest_tool:
        return jsonify({'status': 'error', 'message': 'Tool not initialized'})
    
    try:
        data = request.json
        bssid = data.get('bssid')
        pentest_tool.deauth_attack(bssid)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True) 