from flask_api import FlaskAPI, status, exceptions
from walmar import buscar_rut

app = FlaskAPI(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/buscar_rut/<rut>')
def show_rut(rut):
    resp = buscar_rut(rut)
    if not resp or 'error' in resp:
        return resp, status.HTTP_404_NOT_FOUND
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0')
