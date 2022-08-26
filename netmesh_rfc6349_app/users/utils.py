import os
import requests
import json
import ast

from flask import session, current_app

from netmesh_rfc6349_app.main.utils.netmesh_config_file import NetMeshConfigFile


def login(email, password):
    if not email:
        raise Exception("Email required")

    config_file = NetMeshConfigFile()
    device_config = config_file.load_device_config()
    device_name = device_config.get_device_name()

    credentials = {
        "email": email,
        "password": password,
        "client": device_name
    }
    
    print("credentials", credentials)
    req = requests.post(
        url=f"{current_app.config['RESULTS_SERVER_API_URI']}/user/token/",
        json=credentials)
    req.raise_for_status()
    data = req.json()

    return data


def relogin(email, password):
    if not email:
        raise Exception("Email required")

    credentrials = {
        "email": email,
        "password": password,
    }

    r = requests.post(
        url=f"{current_app.config['RESULTS_SERVER_API_URI']}/auth/login", json=credentrials)
    r.raise_for_status()
    data = r.json()

    if 'access_token' in data:
        token = data['access_token']
        return token
    elif 'error' in data:
        raise Exception(data['error'])
    else:
        raise Exception(str(data))
