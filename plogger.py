from flask import Flask, render_template, request, jsonify
import requests
import socket
from user_agents import parse
import platform
import uuid
import psutil
import json
from datetime import datetime

os_name = platform.system()
hardware_info = platform.uname()

app = Flask(__name__)

# Create an empty list to store user information
user_info_list = []

def get_public_ip():
    try:
        response = requests.get('https://api64.ipify.org?format=json')
        data = response.json()
        public_ip = data['ip']
        return public_ip
    except Exception as e:
        return str(e)

def get_mac_address():
    try:
        interfaces = uuid.UUID(int=uuid.getnode()).hex[-12:]
        mac_address = ":".join([interfaces[e:e + 2] for e in range(0, 11, 2)])
        return mac_address
    except Exception as e:
        return str(e)

def get_local_ip():
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        return local_ip
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    public_ip = request.headers.get('X-Forwarded-For')
    if public_ip is None:
        public_ip = get_public_ip()

    local_ip = get_local_ip()
    mac_address = get_mac_address()

    # Check if the user's information already exists in the list
    user_info = next((info for info in user_info_list if info['public_ip'] == public_ip), None)

    if user_info is None:
        try:
            ip_info_response = requests.get(f'https://ipinfo.io/{public_ip}/json')
            ip_info_data = ip_info_response.json()
            country = ip_info_data.get('country', 'Unknown')
            city = ip_info_data.get('city', 'Unknown')
            provider = ip_info_data.get('org', 'Unknown')
            location = ip_info_data.get('loc', 'Unknown')
        except Exception as e:
            country = 'Unknown'
            city = 'Unknown'
            provider = 'Unknown'
            location = 'Unknown'

        user_agent = parse(request.headers.get('User-Agent'))
        browser = user_agent.browser.family
        browser_version = user_agent.browser.version_string
        os = user_agent.os.family
        os_version = user_agent.os.version_string

        python_version = platform.python_version()

        if user_agent.is_pc:
            device_type = "PC"
        elif user_agent.is_mobile:
            device_type = "Smartphone"
        elif user_agent.is_tablet:
            device_type = "Tablet"
        else:
            device_type = "Unknown"

        memory_info = psutil.virtual_memory()
        total_memory = memory_info.total
        available_memory = memory_info.available
        used_memory = memory_info.used

        cpu_percent = psutil.cpu_percent(interval=1)

        hardware_type = hardware_info.system
        hardware_model = hardware_info.machine

        hardware_manufacturer = "Your Manufacturer"  # Replace with actual manufacturer info

        # Get the current date and time
        timestamp = datetime.now().isoformat()

        # Create a dictionary to store the user's information along with the timestamp
        user_info = {
            "timestamp": timestamp,
            "public_ip": public_ip,
            "local_ip": local_ip,
            "mac_address": mac_address,
            "browser": browser,
            "browser_version": browser_version,
            "os": os,
            "os_version": os_version,
            "python_version": python_version,
            "device_type": device_type,
            "country": country,
            "city": city,
            "provider": provider,
            "location": location,
            "total_memory": total_memory,
            "available_memory": available_memory,
            "used_memory": used_memory,
            "cpu_percent": cpu_percent,
            "hardware_type": hardware_type,
            "hardware_model": hardware_model,
            "hardware_manufacturer": hardware_manufacturer
        }

        # Append the user's information to the list
        user_info_list.append(user_info)

        # Save the user information list to a JSON file
        with open('user_info.json', 'w') as json_file:
            json.dump(user_info_list, json_file, indent=4)

    return render_template('index.html', **user_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
