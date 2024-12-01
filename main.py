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
    
class Notification(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Link to customer
    content = db.Column(db.String(1500), nullable=False)
    customer = db.relationship('customer', backref=db.backref('notification', lazy=True))
    
    
class Notificationsponsor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1500), nullable=False)
    
class Notificationcourier(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1500), nullable=False)
    


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
        
    
class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Link to customer
    delivery_status = db.Column(db.String(50), default="Pending")
    expected_delivery_date = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    customer = db.relationship('customer', backref=db.backref('deliveries', lazy=True))



class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Foreign key to the Customer table
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # Foreign key to the Product table
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of the product
    date_added = db.Column(db.DateTime, default=datetime.utcnow)  # Date when the item was added to the cart
    customer = db.relationship('customer', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))
    
class purchaseditem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Foreign key to the Customer table
    customer = db.relationship('customer', backref=db.backref('purchased_items', lazy=True))
    
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # Foreign key to the Product table
    product = db.relationship('Product', backref=db.backref('purchased_items', lazy=True))
    
    totalprice = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of the product
    refund_status = db.Column(db.String(50), default="Pending")
    refund_reason = db.Column(db.String(100), nullable=True)
    delivery_status = db.Column(db.String(50), default="Pending")



#################################################################################################################################################################################################

@tandtweb.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        address_ = request.form.get('address')

    customer_id = session.get('user_id')
    
    # Fetch cart items for the customer
    cart_items = Cart.query.filter_by(customer_id=customer_id).all()
    if not cart_items:
        flash('Your cart is empty!', 'error')
        return redirect('/cart')
    
   
    
    total_price = sum(item.product.productprice * item.quantity for item in cart_items)

    
    # Update the Money table for the transaction
    new_transaction = Money(type='Add', amount=total_price, purpose='Payment for items')
    db.session.add(new_transaction)
    
    # Create a new delivery entry
    new_delivery = Delivery(address=address_,customer_id=customer_id,expected_delivery_date='TBA')  
    db.session.add(new_delivery)
    
    for item in cart_items:
        purchased_item = purchaseditem(customer_id=customer_id,product_id=item.product.id, totalprice=item.product.productprice * item.quantity, quantity=item.quantity, refund_status='Pending')
        db.session.add(purchased_item)
    
    # Clear the cart after successful checkout
    for item in cart_items:
        db.session.delete(item)
    
    db.session.commit()

    # flash('Checkout successful! Your order is being processed.', 'success')
    return redirect('/customerhome')  # Redirect to customer home or order summary page

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

    # flash('Product added to cart!', 'success')
    return redirect('/products2')



@tandtweb.route('/cart', methods=['GET', 'POST'])
def view_cart():
    customer_id = session.get('user_id')
    
    cart_items = Cart.query.filter_by(customer_id=customer_id).all()
    
    total_price = sum(item.product.productprice * item.quantity for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


#################################################################################################################################################################################################
  
@tandtweb.route('/sncus', methods=['GET', 'POST'])
def noti():
    if request.method == 'POST':
        content = request.form.get('content')
        customer_id = request.form.get('customer_id')
    
        new_noti = Notification(customer_id=customer_id, content=content)
        db.session.add(new_noti)
        db.session.commit()
        
    return render_template('sendnoticus.html')

@tandtweb.route('/noticus', methods=['GET'])
def noticus():
    customer_id = session.get('user_id')
    
    if not customer_id:
        flash('Please log in to view your notification details.', 'error')
        return redirect('/customer')
    
    noti = Notification.query.filter_by(customer_id=customer_id).all()

    if not noti:
        flash('No notification details found.', 'info')
        return redirect('/customerhome')

    return render_template('viewnoticus.html', noti=noti)
       
       
       
@tandtweb.route('/snspo', methods=['GET', 'POST'])
def notispo():
    if request.method == 'POST':
        content = request.form.get('content')

        new_noti = Notificationsponsor(content=content)
        db.session.add(new_noti)
        db.session.commit()
        
    return render_template('sendnotispo.html')

@tandtweb.route('/viewnotispo', methods=['GET'])
def viewnotispo():
    noti_list = Notificationsponsor.query.all()  
    return render_template('viewnotispo.html', noti_list=noti_list)


@tandtweb.route('/sncou', methods=['GET', 'POST'])
def noticou():
    if request.method == 'POST':
        content = request.form.get('content')

        new_noti = Notificationcourier(content=content)
        db.session.add(new_noti)
        db.session.commit()
        
    return render_template('sendnoticou.html')

@tandtweb.route('/viewnoticou', methods=['GET'])
def viewnoticou():
    noti_list = Notificationcourier.query.all()  
    return render_template('viewnoticou.html', noti_list=noti_list)
    
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

@tandtweb.route('/viewfeedbackspon', methods=['GET'])
def view_feedbackspon():
    feedback_list = Feedback.query.all()  
    return render_template('viewfeedbackspon.html', feedback_list=feedback_list)

#################################################################################################################################################################################################
@tandtweb.route('/purchaseditems')
def purchased_items():
    customer_id = session.get('user_id')
    
    purchased_items = purchaseditem.query.filter_by(customer_id=customer_id).all()
    return render_template('purchaseditem.html', purchased_items=purchased_items)


@tandtweb.route('/refund/<int:item_id>', methods=['GET', 'POST'])
def refund_form(item_id):
    purchased_item = purchaseditem.query.get_or_404(item_id)

    if request.method == 'POST':
        refund_reason = request.form.get('reason')
        purchased_item.refund_reason = refund_reason
        purchased_item.refund_status = 'Refund Requested'
        db.session.commit()
        flash('Refund request submitted successfully.', 'success')
        return render_template('customerhome.html')  

    return render_template('refundreason.html',  product_name=purchased_item.product.productname,  item_id=item_id)


@tandtweb.route('/viewref', methods=['GET'])
def view_purchased_items():
    purchased_items = purchaseditem.query.filter(purchaseditem.refund_status == 'Refund Requested').all()
    return render_template('viewref.html', purchased_items=purchased_items)


@tandtweb.route('/accept/<int:item_id>', methods=['GET', 'POST'])
def accept_refund(item_id):
    purchased_item = purchaseditem.query.get_or_404(item_id)
    
    purchased_item.refund_status = 'Refund Accepted'
    
    new_transaction = Money(type='Subtract', amount=purchased_item.totalprice, purpose='Refund')
    db.session.add(new_transaction)
    
    db.session.commit()
    flash('Refund request accepted.', 'success')
    return redirect('/viewref')  

@tandtweb.route('/reject/<int:item_id>', methods=['GET', 'POST'])
def reject_refund(item_id):
    purchased_item = purchaseditem.query.get_or_404(item_id)
    
    purchased_item.refund_status = 'Refund Rejected'
    
    db.session.commit()
    flash('Refund request rejected.', 'danger')
    return redirect('/viewref')  


#################################################################################################################################################################################################


@tandtweb.route('/fundsale', methods=['GET'])
def view_sale():
    transactions = Money.query.filter(Money.purpose == 'Payment for items').all()
    return render_template('fundsale.html', transactions=transactions)


@tandtweb.route('/viewdel', methods=['GET'])
def view_del():
    delivery_list = Delivery.query.all()
    return render_template('viewdel.html', delivery_list=delivery_list)

@tandtweb.route('/viewdelivery', methods=['GET'])
def view_delivery():
    delivery_list = Delivery.query.all()
    return render_template('viewdelivery.html', delivery_list=delivery_list)

@tandtweb.route('/viewdelcus', methods=['GET'])
def delivery_detail():
    customer_id = session.get('user_id')
    if not customer_id:
        flash('Please log in to view your delivery details.', 'error')
        return redirect('/customer')

    deliveries = Delivery.query.filter_by(customer_id=customer_id).all()

    if not deliveries:
        flash('No delivery details found.', 'info')
        return redirect('/customerhome')

    return render_template('viewdelcus.html', deliveries=deliveries)


@tandtweb.route('/editdel/<int:delivery_id>', methods=['GET', 'POST'])
def edit_delivery(delivery_id):
    delivery = Delivery.query.get(delivery_id)
    if not delivery:
        flash('Delivery not found.', 'error')
        return render_template('viewdel.html', delivery=Delivery.query.all())

    if request.method == 'POST':
        # Update delivery details
        delivery.delivery_status = request.form['delivery_status']
        delivery.expected_delivery_date = request.form['expected_delivery_date']

        # Update delivery_status for all associated purchased items
        purchased_items = purchaseditem.query.filter_by(customer_id=delivery.customer_id).all()
        for item in purchased_items:
            item.delivery_status = delivery.delivery_status

        # Commit all changes at once
        db.session.commit()
        flash('Delivery and associated purchased items updated successfully!', 'success')
        return render_template('courierhome.html')

    return render_template('edit_del.html', delivery=delivery)


#################################################################################################################################################################################################



@tandtweb.route('/viewcustomer', methods=['GET'])
def view_customer():
    customer_list = customer.query.all()  
    return render_template('viewcustomer.html', customer_list=customer_list)


@tandtweb.route('/viewcus', methods=['GET'])
def view_cus():
    customer_list = customer.query.all()  
    return render_template('viewcus.html', customer_list=customer_list)


@tandtweb.route('/deletecustomer/<int:customer_id>', methods=['POST', 'GET'])
def delete_customer(customer_id):
    customer_to_delete = customer.query.get(customer_id)
    if customer_to_delete:
        Cart.query.filter_by(customer_id=customer_id).delete()
        db.session.delete(customer_to_delete)
        db.session.commit()
        flash('Customer and associated cart entries deleted successfully!', 'success')
    else:
        flash('Customer not found.', 'error')

    customers = customer.query.all()
    return render_template('viewcustomer.html', customers=customers)

#################################################################################################################################################################################################
@tandtweb.route('/updatefund', methods=['GET', 'POST'])
def updatefund():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        purpose = request.form['purpose']
        action = request.form['action'].lower()  # 'add' or 'subtract'
        
        # Ensure action is valid
        if action not in ['add', 'subtract']:
            flash('Invalid action. Please choose "Add" or "Subtract".', 'error')
            return redirect('/updatefund')
        
        # Create a new transaction
        new_transaction = Money(type=action.capitalize(), amount=amount, purpose=purpose)
        db.session.add(new_transaction)
        db.session.commit()
        
        # Flash success message
        # flash(f'Funds {action}ed successfully!', 'success')
    
    # Calculate total balance
    transactions = Money.query.all()
    total_balance = sum(
        transaction.amount if transaction.type == 'Add' 
        else -transaction.amount
        for transaction in transactions
    )
    
    return render_template('fund.html', transactions=transactions, total_balance=total_balance)


@tandtweb.route('/products', methods=['GET', 'POST'])
def products():
    search_term = None
    if request.method == 'POST':
        search_term = request.form['search_term']
    
    # If there is a search term, filter products based on the name
    if search_term:
        products = Product.query.filter(Product.productname.like(f'%{search_term}%')).all()
    else:
        products = Product.query.all()

    return render_template('customerproduct.html', products=products, search_term=search_term)


@tandtweb.route('/product_admin', methods=['GET', 'POST'])
def product_admin():
    search_term = None
    if request.method == 'POST':
        search_term = request.form['search_term']
    
    # If there is a search term, filter products based on the name
    if search_term:
        products = Product.query.filter(Product.productname.like(f'%{search_term}%')).all()
    else:
        products = Product.query.all()

    return render_template('view_products.html', products=products, search_term=search_term)



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
            image_data = image.read()  
            
            new_product = Product(
                id=id,
                productname=productname,
                productprice=productprice,
                productstock=productstock,
                productpicture=image_data,
                picture_mimetype=mimetype
            )
            
            db.session.add(new_product)
            db.session.commit()
            
            return render_template('add_product.html')  

    return render_template('add_product.html')
  

@tandtweb.route('/product_admin', methods=['GET'])
def view_products():
    products = Product.query.all()
    return render_template('view_products.html', products=products)



@tandtweb.route('/products2', methods=['GET'])
def customerproduct():
    products = Product.query.all()
    return render_template('customerproduct.html', products=products)


@tandtweb.route('/editproduct/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'error')
        return render_template('view_products.html', products=Product.query.all())

    if request.method == 'POST':
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
    product = Product.query.get(product_id)
    
    if product:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    else:
        flash('Product not found.', 'error')

    products = Product.query.all()
    return render_template('view_products.html', products=products)


#################################################################################################################################################################################################
#Log in & sign up
#################################################################################################################################################################################################


@tandtweb.route('/')
def home():
  return render_template('home.html')

@tandtweb.route('/logout')
def logout():
    session.pop('user_id', None)  
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

@tandtweb.route('/confirmcheckout')
def confirmcart():
  return render_template('confirmcheckout.html')

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

