from flask import Flask
from flask import render_template
import docker
app = Flask(__name__)


@app.route('/index')
@app.route('/index.html')
@app.route('/')
def index():
    client = docker.from_env()
    containers = client.api.containers(all=True)
    all_info = []
    for container in containers:
        info = {}
        info['status'] = container['Status']
        info['image'] = container['Image']
        info['name'] = container['Names'][0].strip('/')
        info['state'] = container['State']
        if info['state'] == 'running':
            info['class'] = 'table-primary'
        else:
            info['class'] = 'table-light'
        port = container['Ports']
        if len(port) == 0:
            info['port'] = ''
        else:
            info['port'] = port[0]['PublicPort']
        all_info.append(info)

    return render_template('index.html', title='Home', all_info=all_info)


def start_server():
    app.run()
