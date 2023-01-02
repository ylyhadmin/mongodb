import werkzeug

from file_server import app
from flask import request


@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    file: werkzeug.datastructures.FileStorage = request.files.get('file')
    file.save(f'project/{file.filename}')
    return f'{file.filename}保存成功'


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000)
