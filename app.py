from flask import Flask, render_template,request,redirect,url_for,flash, Response, session
from flask_mysqldb import MySQL,MySQLdb
from flask_paginate import Pagination, get_page_args
from random import sample
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import date
from datetime import datetime

app=Flask(__name__)


#CONFIGURACION DE LA BASE DE DATOS
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='genaro'
app.config['MYSQL_PASSWORD']='password'
app.config['MYSQL_DB']='sistema-ventas'
mysql=MySQL(app)
#-----------------------------------------------------


#CONFIGURACION DE FLASK MAIL
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'gpanelli3@gmail.com'
app.config['MAIL_PASSWORD'] = 'qsxl bfml iosb beta'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail= Mail(app)

app.secret_key="secret_key"
s = URLSafeTimedSerializer('Thisisasecret!')

#-----------------------------------------------------

@app.route('/')
def inicio():
    #conexion a la base de datos
    cursor = mysql.connection.cursor()
    
    #traigo la cantidad de filas que hay en la tabla. Seria la cantidad de registros
    cursor.execute('SELECT COUNT(*) AS total FROM producto')
    row = cursor.fetchone()
    if row:
        count = row[0]  # Acceder al primer elemento de la tupla
        print("Total:", count)
    else:
        print("No se encontraron filas.")

    #utilizo una funcion de pagination, el valor "page", le digo que arranca en la pagina 1 y indico cuantos items quiero por pagina
    page_num=request.args.get('page',1,type=int)
    per_page=5

    #page_num: Este es el número de página que estás viendo actualmente. Por ejemplo, si estás en la primera página, page_num sería 1; si estás en la segunda página, sería 2, y así sucesivamente.
    #per_page: Este valor representa cuántos elementos deseas mostrar en cada página, es decir, el tamaño de tu página.
    #start_index: Este es el índice del primer elemento que se mostrará en la página actual.
    
    start_index=(page_num-1) * per_page +1 
    print(start_index)

    #consulta para traer los productos y plasmarlos en cada pagina
    productos=[]
    sql=(f'SELECT producto.idProducto, producto.nombre, producto.descripcion, categorias.nombre, producto.cantidad, producto.precio FROM producto INNER JOIN categorias ON categorias.idcategorias = id_cat_corresp ORDER BY idProducto DESC LIMIT {per_page} OFFSET {start_index -1}')
    cursor.execute(sql)

    for i in cursor:
        productos.append(i)

    #end_index se calcula como el valor mínimo entre start_index + per_page y count.
    #start_index típicamente representa el índice del primer elemento en una página.
    #per_page indica el número de elementos mostrados por página.
    #count es el número total de elementos en tu conjunto de datos.

    end_index= min(start_index + per_page, count)
    if end_index >count:
        end_index = count

    #paginacion es una funcion de Pagination de Flask donde se juntan todos los datos y se establece los links
    
    pagination=Pagination(page=page_num, total=count, per_page=per_page,
                          display_msg=f"mostrando registros {start_index}- {end_index} de un total de {count}")
    
    mysql.connection.commit()
    categorias=listabebidas()
    cursor.close()


    return render_template("inicio.html", producto=productos, pagination=pagination,categorias=categorias, mensaje="INICIO")
    





@app.route('/agregarProd')
def agregarProd():
    return render_template('agregarProd.html')



@app.route('/ingresarProd', methods=['POST'])
def ingresarProd():
    if request.method == 'POST':
        name=request.form['nombre']
        descr=request.form['descripcion']
        precio=request.form['precio']
        cantidad=request.form['cantidad']
        cat=request.form['categoria']

        nombreMax=""
        nombreMax=name.upper()

        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO producto(nombre,descripcion,precio,cantidad,id_cat_corresp) VALUES(%s,%s,%s,%s,%s)',
                       (nombreMax,descr,precio,cantidad,cat))
        mysql.connection.commit()

        cursor.close()

        
    return redirect(url_for('inicio'))



@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        nombre = request.form.get('idProducto') 
        nuevoPrecio = request.form.get('precio')
        nuevaCantidad = request.form.get('cantidad')

        nombreMax=""
        nombreMax=nombre.upper()

        
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE producto SET precio = %s, cantidad = %s WHERE nombre = %s',
                       (nuevoPrecio, nuevaCantidad, nombreMax))
        
        
        mysql.connection.commit()
        cursor.close()
        print("Actualización correcta")


    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT producto.idProducto, producto.nombre, producto.descripcion, categorias.nombre, producto.cantidad, producto.precio FROM producto INNER JOIN categorias ON categorias.idcategorias = id_cat_corresp")
    productos = cursor.fetchall()
    cursor.close()

    return render_template("update.html", title="Pagina Principal", user="PRODUCTOS INGRESADOS CORRECTAMENTE", productos=productos)

@app.route("/eliminar")
def eliminar():
    nombre = request.form.get('nombre')

    #nombreMax=""
    #nombreMax=nombre.upper()

    cursor = mysql.connection.cursor()
    cursor.execute("delete from producto where nombre = %s", (nombre,))

    mysql.connection.commit()
    cursor.close()
    print("Actualización correcta")

    return render_template("eliminar.html")



def listabebidas():
    data = {}

    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM categorias"
    cursor.execute(sql)
    categorias = cursor.fetchall()
    
    return(categorias)


@app.route("/categ", methods=['POST'])
def seleccion():
    
    cursor = mysql.connection.cursor()
    
   
    id= request.form['pc']
    sql= "SELECT producto.idProducto, producto.nombre, producto.descripcion, categorias.nombre, producto.cantidad, producto.precio FROM producto INNER JOIN categorias ON categorias.idcategorias = id_cat_corresp WHERE id_cat_corresp = %s " 
    cursor.execute(sql,(id,))
    resultados = cursor.fetchall()
    categorias=listabebidas()

    return render_template('seleccionado.html', resultados=resultados, categorias=categorias)


@app.route('/bienvenida')
def bienvenida():
    return render_template('bienvenida.html')


@app.route('/login')
def login():

    return render_template('login.html')


@app.route('/ingreso', methods=['GET', 'POST']) 
def ingreso():


    if request.method == 'POST' and 'nombre' in request.form and 'contra' in request.form:
        usuario = request.form.get('nombre') 
        contra = request.form.get('contra')

        cursor=mysql.connection.cursor()

        cursor.execute("SELECT * from usuario where usuario = %s AND contra = %s", (usuario,contra))
        account=cursor.fetchone()

        if account:
            session['logueado'] = True
            session['usuario'] = usuario

            ingreso=account[4]
            print("holaaaa",ingreso)

            if account[3]==1:
                return redirect(url_for('homeAdmin'))
            #aca agrego la funcionalidad para saber la cantidad de veces que ingreso un usuario
            elif account[3]==2:
                #Fecha actual
                now = datetime.now()
                ingreso+=1
                
                updateQuery=('update usuario set ingresos=%s, fecha=%s where usuario =%s and contra=%s')
                cursor.execute(updateQuery, (ingreso,now,usuario, contra))

                mysql.connection.commit()
                cursor.close()

                return redirect(url_for('usuario'))
         
        else:
            return render_template('login.html', mensaje="USUARIO O CONTRASEÑA INCORRECTA")
                
            


@app.route('/homeAdmin')
def homeAdmin():
    cursor = mysql.connection.cursor()

     #traigo la cantidad de filas que hay en la tabla. Seria la cantidad de registros
    cursor.execute('SELECT COUNT(*) AS total FROM producto')
    row = cursor.fetchone()
    if row:
        count = row[0]  # Acceder al primer elemento de la tupla
        print("Total:", count)
    else:
        print("No se encontraron filas.")

    #utilizo una funcion de pagination, el valor "page", le digo que arranca en la pagina 1 y indico cuantos items quiero por pagina
    page_num=request.args.get('page',1,type=int)
    per_page=5

    #page_num: Este es el número de página que estás viendo actualmente. Por ejemplo, si estás en la primera página, page_num sería 1; si estás en la segunda página, sería 2, y así sucesivamente.
    #per_page: Este valor representa cuántos elementos deseas mostrar en cada página, es decir, el tamaño de tu página.
    #start_index: Este es el índice del primer elemento que se mostrará en la página actual.
    
    start_index=(page_num-1) * per_page +1 
    print(start_index)

    productos=[]
    sql=(f'SELECT producto.idProducto, producto.nombre, producto.descripcion, categorias.nombre, producto.cantidad, producto.precio FROM producto INNER JOIN categorias ON categorias.idcategorias = id_cat_corresp ORDER BY idProducto DESC LIMIT {per_page} OFFSET {start_index -1}')

    cursor.execute(sql)

    for i in cursor:
        productos.append(i)

    end_index= min(start_index + per_page, count)
    if end_index >count:
        end_index = count

    #paginacion es una funcion de Pagination de Flask donde se juntan todos los datos y se establece los links
    
    pagination=Pagination(page=page_num, total=count, per_page=per_page,
                          display_msg=f"mostrando registros {start_index}- {end_index} de un total de {count}")
    
    categorias=listabebidas()



    return render_template('homeAdmin.html', producto=productos, pagination=pagination,categorias=categorias, mensaje='administrador')

    

@app.route("/usuario")
def usuario():
    cursor = mysql.connection.cursor()

     #traigo la cantidad de filas que hay en la tabla. Seria la cantidad de registros
    cursor.execute('SELECT COUNT(*) AS total FROM producto')
    row = cursor.fetchone()
    if row:
        count = row[0]  # Acceder al primer elemento de la tupla
        print("Total:", count)
    else:
        print("No se encontraron filas.")

    #utilizo una funcion de pagination, el valor "page", le digo que arranca en la pagina 1 y indico cuantos items quiero por pagina
    page_num=request.args.get('page',1,type=int)
    per_page=5

    #page_num: Este es el número de página que estás viendo actualmente. Por ejemplo, si estás en la primera página, page_num sería 1; si estás en la segunda página, sería 2, y así sucesivamente.
    #per_page: Este valor representa cuántos elementos deseas mostrar en cada página, es decir, el tamaño de tu página.
    #start_index: Este es el índice del primer elemento que se mostrará en la página actual.
    
    start_index=(page_num-1) * per_page +1 
    print(start_index)

    productos=[]
    sql=(f'SELECT producto.idProducto, producto.nombre, producto.descripcion, categorias.nombre, producto.cantidad, producto.precio FROM producto INNER JOIN categorias ON categorias.idcategorias = id_cat_corresp ORDER BY idProducto DESC LIMIT {per_page} OFFSET {start_index -1}')

    cursor.execute(sql)

    for i in cursor:
        productos.append(i)

    end_index= min(start_index + per_page, count)
    if end_index >count:
        end_index = count

    #paginacion es una funcion de Pagination de Flask donde se juntan todos los datos y se establece los links
    
    pagination=Pagination(page=page_num, total=count, per_page=per_page,
                          display_msg=f"mostrando registros {start_index}- {end_index} de un total de {count}")
    
    categorias=listabebidas()

    return render_template('usuarios.html', producto=productos, pagination=pagination,categorias=categorias, mensaje='usuario')

    



@app.route("/registro")
def registro():
    return render_template("registro.html")



@app.route('/crearRegistro', methods=['GET', 'POST'])
def crearRegistro():   

    email = request.form.get('email') 
    contra = request.form.get('contra')

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT usuario FROM usuario')
    resultados = cursor.fetchall()

    for resultado in resultados: 
        if resultado[0] == email:
            return render_template('registro.html', mensaje='Este usuario ya se encuentra registrado')

        else:
            cursor.execute('INSERT INTO usuario(usuario,contra,id_rol) VALUES(%s,%s,%s)',(email,contra,2))
            mysql.connection.commit()
            return render_template("login.html")




@app.route('/usuAdministrar')
def usuAdministrar():
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT usuario,contra,ingresos,fecha from usuario")
    usuarios=cursor.fetchall()

    return render_template("usuAdministrar.html", usuario=usuarios)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
    

if __name__ == '__main__':
    app.run(port=8000, debug=True)


#PARA DOCKER
#if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=True)
