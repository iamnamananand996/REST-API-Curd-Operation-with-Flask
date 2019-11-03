from flask import Flask, jsonify, request, session
from flaskext.mysql import MySQL
import json


# Login Firebase
import pyrebase


config = {
    "apiKey": "AIzaSyArRg7oyMC2r4uddo8PyCqFMaD8EM108OM",
    "authDomain": "mainapp-70f63.firebaseapp.com",
    "databaseURL": "https://mainapp-70f63.firebaseio.com",
    "projectId": "mainapp-70f63",
    "storageBucket": "mainapp-70f63.appspot.com",
    "messagingSenderId": "487036226421"
}


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()


app = Flask(__name__)


app.config['SECRET_KEY'] = 'ec830e5ae057c5b08f5a435a7b13e891'


# Config MySQL
app.config['MYSQL_DATABASE_HOST'] = "localhost"
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'api_blog'


# init MYSQL
mysql = MySQL()
mysql.init_app(app)


@app.route('/')
def index():
    try:
        if session['username'] :
            return jsonify({'username' : session['username']})
    except:
        return jsonify({'res' : 'user not loged in'})




@app.route('/add',methods=['POST'])
def add():
    try:
        if session['username']:
            data = request.get_json()
            blog_title = data['blog_title']
            description = data['description']

            conn = mysql.connect()
            cursor = conn.cursor()
            
            if(cursor.execute("INSERT INTO blog(user_id, blog_title, desciption) VALUES(%s,%s,%s)",(session['username'], blog_title, description))):
                conn.commit()
                cursor.close()


            return jsonify({'data' : data,
                            'username' : session['username']})
    except:
        return jsonify({'res' : 'user not loged in'})


@app.route('/login',methods=['POST'])
def login():
    try:
        if session['username']:
            return jsonify({"logged_in" : session['logged_in'],
                            "username" : session['username']})
    except:
        data = request.get_json()
        print(data)
        if len(data) > 0:
            email = data['username']
            password = data['password']
            user = auth.sign_in_with_email_and_password(email, password)
            if user:
                session['logged_in'] = True
                session['username'] = email
                
                return jsonify({"logged_in" : session['logged_in'],
                                "username" : session['username']})


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({"res" : "logout success"})



@app.route('/view',methods=['GET'])
def view():

    conn = mysql.connect()
    cursor = conn.cursor()


    query = "SELECT * FROM `blog`"
    result = cursor.execute(query)

    # print(result,cursor.fetchall())

    all_post = []

    for data in cursor.fetchall():
        res = { "username" : data[0],
                "post_id ": data[1],
                "blog_title" : data[2],
                "description" : data[3]
              }
        all_post.append(res)
            
    return jsonify({'blog_post' : all_post})

@app.route('/update',methods=['PATCH'])
def update():

    try:
        if session['username'] :

            data = request.get_json()

            conn = mysql.connect()
            cursor = conn.cursor()

            query = """UPDATE blog SET blog_title = %s ,desciption = %s WHERE blog.post_id = %s and user_id = %s """
            values = (data['blog_title'], data['description'], data['post_id'],session['user_id'])
            if(cursor.execute(query,values)):
                print('data updated')
                conn.commit()
                cursor.close()
                    
            return jsonify({'data' : data})

    except:
        return jsonify({'user not loged in'})



@app.route('/delete',methods=['DELETE'])
def delete():

    try:
        if session['username'] :

            data = request.get_json()
            conn = mysql.connect()
            cursor = conn.cursor()
            
            query = """DELETE FROM blog WHERE post_id = %s and user_id = %s"""
            
            values = (data['post_id'],session['username'])
            if(cursor.execute(query,values)):
                print('data deleted')
                conn.commit()
                cursor.close()        
                return jsonify({'res' : "data deleted"})

    except:
        return jsonify({'user not loged in'})





if __name__ == '__main__':
    app.run(debug=True)


