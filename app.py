from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Cambia esto por una clave secreta única


# Ruta para mostrar el menú
@app.route('/')
def index():
    conn = sqlite3.connect('menu.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM platos')
    platos = cursor.fetchall()
    conn.close()
    return render_template('index.html', platos=platos)


@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        descripcion = request.form['descripcion']

        # Procesar la imagen
        imagen = request.files['imagen']
        if imagen and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagen.save(ruta_imagen)
            imagen_url = f'/static/uploads/{filename}'
        else:
            return 'Formato de imagen no permitido', 400

        # Guardar en la base de datos
        con = sqlite3.connect('menu.db')
        cur = con.cursor()
        cur.execute("INSERT INTO platos (nombre, precio, imagen_url, descripcion) VALUES (?, ?, ?, ?)",
                    (nombre, precio, imagen_url, descripcion))
        con.commit()
        con.close()

        return redirect(url_for('index'))

    return render_template('agregar.html')

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']


        # Aquí puedes poner tus credenciales de administrador
        if usuario == 'admin' and contrasena == '1234':  # Cambia esto por una validación más segura
            session['usuario'] = usuario  # Guardamos el usuario en la sesión
            return redirect(url_for('agregar'))  # Redirigimos al administrador al formulario de agregar plato
        else:
            return 'Usuario o contraseña incorrectos', 400  # Error si no coincide

    return render_template('login.html')
@app.route('/editar/<int:plato_id>', methods=['GET', 'POST'])
def editar(plato_id):
    con = sqlite3.connect('menu.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM platos WHERE id = ?', (plato_id,))
    plato = cur.fetchone()

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        descripcion = request.form.get('descripcion')

        # Procesar imagen
        imagen = request.files.get('imagen')
        if imagen and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagen.save(imagen_path)
            imagen_url = f'/static/uploads/{filename}'
        else:
            imagen_url = plato[3]  # mantener la anterior si no se sube nueva

        cur.execute('''UPDATE platos SET nombre = ?, precio = ?, imagen_url = ?, descripcion = ? WHERE id = ?''',
                    (nombre, precio, imagen_url, descripcion, plato_id))
        con.commit()
        con.close()
        return redirect(url_for('index'))

    con.close()
    return render_template('editar.html', plato=plato)
@app.route('/eliminar/<int:plato_id>', methods=['POST'])
def eliminar(plato_id):
    con = sqlite3.connect('menu.db')
    cur = con.cursor()
    cur.execute('DELETE FROM platos WHERE id = ?', (plato_id,))
    con.commit()
    con.close()
    return redirect(url_for('index'))

# Ruta de cierre de sesión
@app.route('/logout')
def logout():
    session.pop('usuario', None)  # Elimina la sesión del usuario
    return redirect(url_for('index'))  # Redirige al menú principal

from werkzeug.utils import secure_filename
import os
# Configuración para cargar archivos
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Carpeta donde se guardarán las imágenes
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Extensiones permitidas

# Función para verificar si el archivo tiene una extensión permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Crear la carpeta 'uploads' si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(debug=True)