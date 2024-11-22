from flask import Flask,render_template,request,session

#database
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


db =SQLAlchemy()
DB_NAME ="database.sqlite3"

def create_database():
  db.create_all()
  print("databases created")

tandtweb=Flask(__name__)
tandtweb.secret_key='12345ABC'
tandtweb.config['SQLALCHEMY_DATABASE_URI']=f'sqlite:///{DB_NAME}'
db.init_app(tandtweb)


with tandtweb.app_context():
  create_database()
  
  
#################################################################################################################################################################################################  
#Tables
#################################################################################################################################################################################################

class customer(db.Model,UserMixin):
  id=db.Column(db.Integer,primary_key=True)
  password=db.Column(db.String(150))
  email=db.Column(db.String(100),unique=True)
  ph=db.Column(db.String(150),unique=True)
  gender=db.Column(db.String(150))
  dob=db.Column(db.DateTime(),default=datetime.utcnow)
  
#################################################################################################################################################################################################
  
  
#################################################################################################################################################################################################
#Log in & sign up
#################################################################################################################################################################################################


@tandtweb.route('/')
def home():
  return render_template('home.html')


@tandtweb.route('/aboutus')
def aboutus():
  return render_template('aboutus.html')

#admin login function
@tandtweb.route('/admin', methods=['GET', 'POST'])
def loginadmin():
    if request.method == 'POST':
        adminusername = request.form['username']
        adminpassword = request.form['password']
        
        #only this id can login as admin
        admin_access = {
            '1211111953': 'shah'
        }

        if adminusername in admin_access and adminpassword == admin_access[adminusername]:
            session['username'] = adminusername
            return render_template('adminhome.html')
        else:
            return render_template('adminfaillogin.html')

    return render_template('adminlogin.html')
  
  
  
#courier login function
@tandtweb.route('/courier', methods=['GET', 'POST'])
def logincourier():
    if request.method == 'POST':
        courierusername = request.form['username']
        courierpassword = request.form['password']
        
        #only this id can login as courier
        courier_access = {
            '1211111953': 'shah'
        }

        if courierusername in courier_access and courierpassword == courier_access[courierusername]:
            session['username'] = courierusername
            return render_template('courierhome.html')
        else:
            return render_template('courierfaillogin.html')

    return render_template('courierlogin.html')
  
#sponsor login function
@tandtweb.route('/sponsor', methods=['GET', 'POST'])
def loginsponsor():
    if request.method == 'POST':
        sponsorusername = request.form['username']
        sponsorpassword = request.form['password']
        
        #only this id can login as sponsor
        sponsor_access = {
            '1211111953': 'shah'
        }

        if sponsorusername in sponsor_access and sponsorpassword == sponsor_access[sponsorusername]:
            session['username'] = sponsorusername
            return render_template('sponsorhome.html')
        else:
            return render_template('sponsorfaillogin.html')

    return render_template('sponsorlogin.html')
  
  
#customer login
@tandtweb.route('/customer',methods=['GET', 'POST'])
def customerlogin():
  if request.method=='POST':
    id=request.form['id']
    password=request.form['password']
    
    user=customer.query.filter_by(id=id).first()
    if user and user.password==password:
      session['user_id']=user.id
      return render_template("customerhome.html")
    else:
      return render_template("customerloginfail.html")
    
  return render_template("customerlogin.html")


#customer sign up
@tandtweb.route('/customersignup',methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        email = request.form['email']
        ph=request.form['ph']
        gender = request.form['gender']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        
        
        new_customer = customer(
        id=id,
        password=password,
        email=email,
        ph=ph,
        gender=gender,
        dob=dob
      )
        
        db.session.add(new_customer)
        db.session.commit()

        return render_template('customerlogin.html')
    
    return render_template('customersignup.html')
  
#################################################################################################################################################################################################

if __name__ == '__main__':
    tandtweb.run(debug=True)

