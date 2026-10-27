
from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)



def conectar_bd():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="practica_flask",
        connection_timeout=5
    )



@app.route("/")
def inicio():
    return render_template("productos.html")



@app.route("/registrar", methods=["POST"])
def registrar():
    nombre = request.form.get("nombre", "").strip()

    try:
        precio = float(request.form.get("precio", ""))
        stock = int(request.form.get("stock", ""))
    except ValueError:
        return "Error: el precio y el stock deben ser números.", 400

    if not nombre:
        return "Error: el nombre es obligatorio.", 400

    if precio <= 0 or stock < 0:
        return "Error: revisa el precio y el stock.", 400

    conexion = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO productos (nombre, precio, stock)
            VALUES (%s, %s, %s)
            """,
            (nombre, precio, stock)
        )

        conexion.commit()
        cursor.close()

        return redirect("/productos")

    except mysql.connector.Error:
        if conexion is not None and conexion.is_connected():
            conexion.rollback()

        return "No se pudo guardar el producto. Verifica MySQL e inténtalo de nuevo.", 500

    finally:
        if conexion is not None and conexion.is_connected():
            conexion.close()



@app.route("/productos")
def listar_productos():
    conexion = conectar_bd()

    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre, precio, stock FROM productos"
        )
        productos = cursor.fetchall()
        cursor.close()

        resultado = """
        <h1>Productos registrados</h1>
        <table border="1" cellpadding="8">
            <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Precio</th>
                <th>Stock</th>
                <th>Acciones</th>
                </tr>
        """

        for producto in productos:
            resultado += f"""
<tr>
    <td>{producto[0]}</td>
    <td>{producto[1]}</td>
    <td>{producto[2]}</td>
    <td>{producto[3]}</td>
    
<td>
    <a href="/editar/{producto[0]}">Editar</a>

    <form action="/eliminar/{producto[0]}" method="POST">
        <button type="submit">Eliminar</button>
    </form>
</td>

</tr>
"""

        resultado += """
        </table>
        <p><a href="/">Registrar otro producto</a></p>
        """

        return resultado

    finally:
        conexion.close()



@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar_producto(id):
    conexion = conectar_bd()

    try:
        cursor = conexion.cursor()
        cursor.execute(
            "DELETE FROM productos WHERE id = %s",
            (id,)
        )
        conexion.commit()
        cursor.close()

    finally:
        conexion.close()

    return redirect("/productos")




@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    conexion = conectar_bd()

    try:
        cursor = conexion.cursor()

        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()

            try:
                precio = float(request.form.get("precio", ""))
                stock = int(request.form.get("stock", ""))
            except ValueError:
                return "El precio y el stock deben ser números válidos.", 400

            if not nombre:
                return "El nombre es obligatorio.", 400

            if precio <= 0 or stock < 0:
                return "El precio debe ser mayor que cero y el stock no puede ser negativo.", 400

            cursor.execute(
                """
                UPDATE productos
                SET nombre = %s, precio = %s, stock = %s
                WHERE id = %s
                """,
                (nombre, precio, stock, id)
            )

            conexion.commit()
            return redirect("/productos")

        cursor.execute(
            "SELECT id, nombre, precio, stock FROM productos WHERE id = %s",
            (id,)
        )

        producto = cursor.fetchone()

        if producto is None:
            return "Producto no encontrado.", 404

        return render_template("editar.html", producto=producto)

    finally:
        conexion.close()


if __name__ == "__main__":
    app.run(debug=True)
