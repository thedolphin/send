import io, os, xattr
import random, re

from flask import Flask, request, redirect, render_template, flash, send_file, url_for, abort
from flask import Markup
from werkzeug import secure_filename
from pyAesCrypt import encryptStream, decryptStream

application = Flask(__name__)
application.config.from_pyfile('app.cfg')

valid_code = re.compile('[a-zA-Z0-9]+')

def randomstring(length=8):
    chars=list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    return ''.join([random.choice(chars) for _ in range(length)])


@application.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == "GET":
        return render_template('upload.html')

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(application.config['BASE_URL'])
        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(application.config['BASE_URL'])

        filename = randomstring(16)
        enc_key = randomstring(16)
        filepath = os.path.join(application.config['UPLOAD_FOLDER'], filename)

        with open(filepath, "wb") as output:
            encryptStream(file, output, enc_key, 4096)

        result_url = '{0}{1}/{2}'.format(application.config['BASE_URL'], filename, enc_key)

        flash(Markup('<a href="{0}">{0}</a>'.format(result_url)), 'success')
        xattr.setxattr(filepath, 'user.filename', secure_filename(file.filename).encode('latin-1'))
        xattr.setxattr(filepath, 'user.contenttype', file.content_type.encode('latin-1'))

        if request.referrer:
            return redirect(application.config['BASE_URL'])
        else:
            return result_url


@application.route('/<string:path>/<string:enc_key>')
def serve(path, enc_key):

    if valid_code.fullmatch(path) == None or valid_code.fullmatch(enc_key) == None:
        flash('A-ha-ha!', 'warning')
        return redirect(application.config['BASE_URL'])

    filepath = os.path.join(application.config['UPLOAD_FOLDER'], path)

    if not os.path.exists(filepath):
        flash("No such file", "danger")
        return redirect(application.config['BASE_URL'])

    filesize = os.path.getsize(filepath)

    filename = xattr.getxattr(filepath, 'user.filename').decode('latin-1')
    content_type = xattr.getxattr(filepath, 'user.contenttype').decode('latin-1')

    output = io.BytesIO()
    with open(filepath, "rb") as input:
        decryptStream(input, output, enc_key, 4096, filesize)

    output.seek(0)

    retval = send_file(output,
                     mimetype=content_type,
                     as_attachment=False if content_type.startswith('image/') else True,
                     attachment_filename=filename,
                     cache_timeout=0)
    os.unlink(filepath)
    return retval


@application.route('/<path:path>')
def default(path):
    abort(404)

if __name__ == '__main__':
    application.run()
