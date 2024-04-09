from flask import Flask, render_template,request,redirect,url_for,flash
from flask_mysqldb import MySQL
from flask_paginate import Pagination, get_page_args


app=Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='genaro'
app.config['MYSQL_PASSWORD']='password'
app.config['MYSQL_DB']='sistema-ventas'

mysql=MySQL(app)

app.secret_key = 'mysectrectkey'


@app.route('/')
def index():
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
    sql=(f'SELECT producto.idProducto, producto.nombre, producto.descripcion, categorias.nombre, producto.cantidad, producto.precio FROM producto INNER JOIN categorias ON categorias.idcategorias = id_cat_corresp ORDER BY idProducto ASC LIMIT {per_page} OFFSET {start_index -1}')
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
    cursor.close()


    return render_template("index.html", producto=productos, pagination=pagination)





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
        #img=request.form['imagen']

        nombreMax=""
        nombreMax=name.upper()

        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO producto(nombre,descripcion,precio,cantidad,id_cat_corresp) VALUES(%s,%s,%s,%s,%s)',
                       (nombreMax,descr,precio,cantidad,cat))
        mysql.connection.commit()
    

        cursor.close()
        
    return redirect(url_for('index'))






@app.route('/categoria')
def categoria():
    cursor=mysql.connection.cursor()

    prodCat=[]
    sql=('SELECT * FROM producto')
    cursor.execute(sql)
    
    for i in cursor:
        prodCat.append(i)

    return render_template("categoria.html", categoria=prodCat)

if __name__ == '__main__':
    app.run(port=8000, debug=True)



