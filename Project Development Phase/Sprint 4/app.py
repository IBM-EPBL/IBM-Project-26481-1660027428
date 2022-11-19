from flask import Flask, render_template, request,session
import os
from werkzeug.utils import secure_filename
import numpy as np
from keras.models import load_model
from keras.utils import load_img,img_to_array
import sqlite3
import keras

UPLOAD_FOLDER=os.path.join('static','uploads')
ALLOWED_EXTENSIONS = {'jpg','png','jpeg'}


app = Flask( __name__, template_folder="templates")
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.secret_key = "nutrition"

import ibm_db
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30376;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=dxr29301;PWD=p3zuFER2nT87cpK5",'','')


@app.route('/')
def home():
  return render_template('HOME.html')

@app.route('/signup')
def signup():
  return render_template('signup.html')
 
@app.route('/adduser',methods = ['POST', 'GET'])
def adduser():

  print("Iam inside the register method")
  if request.method == 'POST':
    print("Iam inside the post method")
    Name = request.form['Name']
    Email = request.form['Mail']
    Mobile = request.form['Mobile']
    Password = request.form['Password']
    ConfirmPassword = request.form['ConfirmPassword']
    print(Name)
    sql = "SELECT * FROM profiles WHERE Name =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,Name)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)

    if account:
      return render_template('login.html', msg="You are already a member, please login using your details")
    else:
      insert_sql = "INSERT INTO profiles VALUES (?,?,?,?,?)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, Name)
      ibm_db.bind_param(prep_stmt, 2, Email)
      ibm_db.bind_param(prep_stmt, 3, Mobile)
      ibm_db.bind_param(prep_stmt, 4, Password)
      ibm_db.bind_param(prep_stmt, 5, ConfirmPassword)
      ibm_db.execute(prep_stmt)
  return render_template('details.html', msg="Profile was created successfully")

@app.route('/details')
def details():
  return render_template('details.html')

@app.route('/adddetails',methods = ['POST', 'GET'])
def adddetails():

  if request.method == 'POST':
    FirstName = request.form['FirstName']
    LastName = request.form['LastName']
    Age = request.form['Age']
    Weight = request.form['Weight']
    Height = request.form['Height']
    print(FirstName)
    sql = "SELECT * FROM details WHERE FirstName =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,FirstName)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)

    insert_sql = "INSERT INTO details VALUES (?,?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, FirstName)
    ibm_db.bind_param(prep_stmt, 2, LastName)
    ibm_db.bind_param(prep_stmt, 3, Age)
    ibm_db.bind_param(prep_stmt, 4, Weight)
    ibm_db.bind_param(prep_stmt, 5, Height)
    ibm_db.execute(prep_stmt)
  return render_template('workspace.html')

@app.route('/')  # route to display the home page
def workspace():
    return render_template('workspace.html')  # rendering the home page

@app.route('/calculation')
def calculation():
  return render_template('calculation.html')

@app.route('/classify')
def classify():
    return render_template('classify.html',data="working")

@app.route('/imageprediction')
def imageprediction():
    return render_template('imageprediction.html')

@app.route('/addimageprediction', methods=['POST']
)  # routes to the index imageprediction
def addimageprediction():
    if request.method=="POST":
        img  = request.files["image"]
        img_filename = secure_filename(img.filename)
        img.save(os.path.join(app.config['UPLOAD_FOLDER'],img_filename))
        session['uploaded_img_filepath'] = os.path.join(app.config['UPLOAD_FOLDER'],img_filename)
        img_filepath = session.get('uploaded_img_filepath',None)
        image_pred = launch(img_filepath)
        print(img_filepath)
        return render_template("imageprediction.html",value=img_filepath,pred=image_pred[0],content=image_pred,flag=True)
    else:
        return render_template("classify.html",data="image not send or error")

def launch(img_filepath):
    model = load_model('nutrition.h5')
    img = load_img(img_filepath, target_size=(64, 64))  # load and reshaping the image
    x = img_to_array(img)  # converting image to an array
    x = np.expand_dims(x, axis=0)  # changing the dimensions of the imag
    predict_x = model.predict(x)
    classes_x = np.argmax(predict_x)
    index = ['Apple', 'Banana', 'Orange', 'Pineapple', 'Watermelon']
    values = nutrition(index[classes_x])
    return [index[classes_x], values]
  
def nutrition(x):
    conn = sqlite3.connect('nutro.db')
    cursor = conn.execute(f'''SELECT * FROM nutro WHERE FRUIT=="{x}"''')
    rec = cursor.fetchall()[0]
    return rec



@app.route('/login')
def login():
  return render_template('login.html')

if( __name__ == 'main'):
  app.run()