from flask import Flask,render_template,request,session,flash,redirect
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort

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
  
import base64
  
@tandtweb.template_filter('b64encode')
def b64encode_filter(value):
    if value:
        return base64.b64encode(value).decode('utf-8')  # Convert bytes to a base64 string
    return ''
  
  
#################################################################################################################################################################################################  
#Tables
#################################################################################################################################################################################################

class customer(db.Model,UserMixin):
  id=db.Column(db.Integer, primary_key=True)
  name=db.Column(db.String(150))
  password=db.Column(db.String(150))
  email=db.Column(db.String(100),unique=True)
  ph=db.Column(db.String(150),unique=True)
  gender=db.Column(db.String(150))
  dob=db.Column(db.DateTime(),default=datetime.utcnow)
  
  
class Feedback(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    ph = db.Column(db.String(150), unique=True, nullable=False)
    content = db.Column(db.String(1500), nullable=False)
    date=db.Column(db.DateTime(),default=datetime.utcnow)
    
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the product
    productname = db.Column(db.String(150), nullable=False)
    productprice = db.Column(db.Float, nullable=False)
    productdate = db.Column(db.DateTime, default=datetime.utcnow)
    productstock = db.Column(db.Integer, nullable=False)
    productpicture = db.Column(db.LargeBinary, nullable=False)  # Stores the binary data of the image
    picture_mimetype = db.Column(db.String(50), nullable=False)  # To store the image format (e.g., 'image/jpeg')
  
class Money(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))  # 'Add' or 'Subtract'
    amount = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Foreign key to the Customer table
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # Foreign key to the Product table
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of the product
    date_added = db.Column(db.DateTime, default=datetime.utcnow)  # Date when the item was added to the cart
    customer = db.relationship('customer', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))

#################################################################################################################################################################################################
@tandtweb.route('/removefromcart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    cart_item = Cart.query.get(item_id)
    
    if cart_item:
        product = cart_item.product
        product.productstock += cart_item.quantity
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart, quantity updated back to stock!', 'success')
    else:
        flash('Item not found in the cart.', 'error')
    return redirect('/cart')



@tandtweb.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    customer_id = session.get('user_id')
    if not customer_id:
        flash('Please log in to add products to your cart.', 'error')
        return redirect('/customer')  

    try:
        quantity = int(request.form['quantity'])
        if quantity < 1:
            flash('Quantity must be at least 1.', 'error')
            return redirect('/products2')
    except (KeyError, ValueError):
        flash('Invalid quantity.', 'error')
        return redirect('/products2')

    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect('/products2')
    if product.productstock < quantity:
        flash('Not enough stock available.', 'error')
        return redirect('/products2')

 
    cart_item = Cart.query.filter_by(customer_id=customer_id, product_id=product_id).first()
    if cart_item:
       
        cart_item.quantity += quantity
    else:
       
        cart_item = Cart(customer_id=customer_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
   
    product.productstock -= quantity
    db.session.commit()

    flash('Product added to cart!', 'success')
    return redirect('/products2')



@tandtweb.route('/cart', methods=['GET', 'POST'])
def view_cart():
    customer_id = session.get('user_id')
    
    cart_items = Cart.query.filter_by(customer_id=customer_id).all()
    
    total_price = sum(item.product.productprice * item.quantity for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


#################################################################################################################################################################################################
  
@tandtweb.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        ph = request.form.get('ph')
        content = request.form.get('content')
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')

        if not name or not email or not ph or not content:
            flash('All fields are required!', 'error')
            return render_template('feedback.html', name=name, email=email, ph=ph, content=content)

        new_feedback = Feedback(name=name, email=email, ph=ph, content=content)
        db.session.add(new_feedback)
        db.session.commit()

        flash('Thank you for your feedback!', 'success')
        return render_template('feedback.html')

    return render_template('feedback.html')

@tandtweb.route('/viewfeedback', methods=['GET'])
def view_feedback():
    feedback_list = Feedback.query.all()  
    return render_template('viewfeedback.html', feedback_list=feedback_list)

#################################################################################################################################################################################################

@tandtweb.route('/updatefund', methods=['GET', 'POST'])
def updatefund():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        purpose = request.form['purpose']
        action = request.form['action']
        
        if action == 'subtract':
            amount = -amount  
        
        new_transaction = Money(type=action.capitalize(), amount=amount, purpose=purpose)
        db.session.add(new_transaction)
        db.session.commit()
        
        total_balance = db.session.query(db.func.sum(Money.amount)).scalar() or 0
        flash(f'Fund {action}ed successfully! Total Balance: ${total_balance:.2f}', 'success')
    
    total_balance = db.session.query(db.func.sum(Money.amount)).scalar() or 0
    transactions = Money.query.all()
    
    return render_template('fund.html', transactions=transactions, total_balance=total_balance)

#################################################################################################################################################################################################

@tandtweb.route('/addprod', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        id = request.form['id']
        productname = request.form['productname']
        productprice = float(request.form['productprice'])
        productstock = int(request.form['productstock'])
        image = request.files['productpicture']
        
        if image:
            filename = secure_filename(image.filename)
            mimetype = image.mimetype
            image_data = image.read()  # Read the binary data
            
            # Create a new Product instance
            new_product = Product(
                id=id,
                productname=productname,
                productprice=productprice,
                productstock=productstock,
                productpicture=image_data,
                picture_mimetype=mimetype
            )
            
            # Save to the database
            db.session.add(new_product)
            db.session.commit()
            
            return render_template('add_product.html')  # Redirect to the same page or another

    return render_template('add_product.html')
  

@tandtweb.route('/products', methods=['GET'])
def view_products():
    # Fetch all products from the database
    products = Product.query.all()
    return render_template('view_products.html', products=products)

@tandtweb.route('/products2', methods=['GET'])
def customerproduct():
    # Fetch all products from the database
    products = Product.query.all()
    return render_template('customerproduct.html', products=products)


@tandtweb.route('/editproduct/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'error')
        return render_template('view_products.html', products=Product.query.all())

    if request.method == 'POST':
        # Get updated data from form
        product.productname = request.form['productname']
        product.productprice = float(request.form['productprice'])
        product.productstock = int(request.form['productstock'])
        image = request.files['productpicture']
        
        if image:
            product.productpicture = image.read()
            product.picture_mimetype = image.mimetype

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return render_template('view_products.html', products=Product.query.all())

    return render_template('edit_product.html', product=product)


@tandtweb.route('/deleteproduct/<int:product_id>', methods=['POST', 'GET'])
def delete_product(product_id):
    # Fetch the product by ID
    product = Product.query.get(product_id)
    
    if product:
        # Delete the product from the database
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    else:
        flash('Product not found.', 'error')

    # Fetch the updated list of products after deletion
    products = Product.query.all()
    return render_template('view_products.html', products=products)


#################################################################################################################################################################################################
#Log in & sign up
#################################################################################################################################################################################################


@tandtweb.route('/')
def home():
  return render_template('home.html')

@tandtweb.route('/customerhome')
def customerhome():
  return render_template('customerhome.html')

@tandtweb.route('/adminhome')
def adminhome():
  return render_template('adminhome.html')

@tandtweb.route('/sponsorhome')
def sponsorhome():
  return render_template('sponsorhome.html')

@tandtweb.route('/courierhome')
def courierhome():
  return render_template('courierhome.html')


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
            '1211111953': 'shah',
            '1211109514': 'ami',
            '1211109601': 'batrisya',
            '1211108832': 'natasha'
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
            '1211111953': 'shah',
            '1211109514': 'ami',
            '1211109601': 'batrisya',
            '1211108832': 'natasha'
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
            '1211111953': 'shah',
            '1211109514': 'ami',
            '1211109601': 'batrisya',
            '1211108832': 'natasha'
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
        name= request.form['name']
        password = request.form['password']
        email = request.form['email']
        ph=request.form['ph']
        gender = request.form['gender']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        
        
        new_customer = customer(
        id=id,
        name=name,
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

