from flask_app import app
from flask import render_template, redirect, request, session, flash, url_for
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from flask_app.models.user import User
from flask_app.models.item import Item

import paypalrestsdk

from flask_mail import Mail, Message
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sonilamertiri1@gmail.com'
app.config['MAIL_PASSWORD'] = 'jsnt mvqe tdfd pihb'
app.config['MAIL_DEFAULT_SENDER'] = ('Your Name', 'sonilamertiri1@gmail.com')


# sundbox personal

# F%o1Zm0I
# sb-8vljf29776541@personal.example.com

# ketu krijojme routet per userin

@app.route('/register')
def registerPage():
    if 'user_id' in session:
        return redirect('/')
    return render_template('register.html')

@app.route('/login', methods=['GET'])
def loginPage():
    if 'user_id' in session:
        return redirect('/')
    return render_template('login.html')


@app.route('/register', methods=['POST'])
def register():
    if 'user_id' in session:
        return redirect('/')
    if not User.validate_userRegister(request.form):
        return redirect(request.referrer)
    user= User.get_user_by_email(request.form)
    if user:
        flash('This account already exist!', 'emailRegister')
        return redirect(request.referrer)
    data={
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': bcrypt.generate_password_hash(request.form['password'])  
    }
    session['user_id']=User.create(data)
    return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    if 'user_id' in session:
        return redirect('/')
    if not User.validate_user(request.form):
        return redirect(request.referrer)
    
    user= User.get_user_by_email(request.form)
    if not user:
        flash('This email doesnt exist!', 'emailLogin')
        return redirect(request.referrer)
    
    if not bcrypt.check_password_hash(user['password'], request.form['password']):
        flash('Incorrect password!', 'passwordLogin')
        return redirect(request.referrer)
    
    session['user_id']= user['id']
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# paypal

@app.route('/checkout/paypal/<int:id>')
def checkoutPaypal(id):
    if 'user_id' not in session:
        return redirect('/')
    data={
        'id': id
    }
    item=Item.get_item_by_id(data)
    taksa=2
    totalPrice=item['price'] + taksa
    try:
        paypalrestsdk.configure({
            "mode": "sandbox",
            "client_id": "AQtIlqp4cJJNLjDFvJQH_4cmmYj-srYBVIP0jjgp5-8wMsCWBYv51HB74GRc5VXo0JijTqEMw3sHy70-",
            "client_secret": "ELpwmVruy5GUnQHbFr95TC39upzGN0qro4yrXhErp7DYZwOZjgX9LSbZONTFjUz6kVVOBT_KYCpyrvf-"
        })
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": totalPrice,
                    "currency": "USD"
                },
                "description": f"Pagese per produktin {item} duke perfshire edhe shipping fee {taksa}!"
            }],
            "redirect_urls": {
                "return_url": url_for('paymentSuccess', item_id=id, totalPrice=totalPrice, _external=True),
                "cancel_url": "http://example.com/cancel"
            }
        })

        if payment.create():
            approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
            print("Redirect URL:", approval_url)  
            return redirect(approval_url)
        else:
            flash('Something went wrong with your payment', 'creditCardDetails')
            return redirect(request.referrer)
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'creditCardDetails')
        return redirect(request.referrer)


@app.route("/success", methods=["GET"])
def paymentSuccess():
    payment_id = request.args.get('paymentId', '')
    payer_id = request.args.get('PayerID', '')
    # item_id = request.args.get('item_id', '')
    # print("Item ID:", item_id)
    try:
        paypalrestsdk.configure({
            "mode": "sandbox",
            "client_id": "AQtIlqp4cJJNLjDFvJQH_4cmmYj-srYBVIP0jjgp5-8wMsCWBYv51HB74GRc5VXo0JijTqEMw3sHy70-",
            "client_secret": "ELpwmVruy5GUnQHbFr95TC39upzGN0qro4yrXhErp7DYZwOZjgX9LSbZONTFjUz6kVVOBT_KYCpyrvf-"
        })
        payment = paypalrestsdk.Payment.find(payment_id)
        if not payment.execute({"payer_id": payer_id}):  #because of one unexpected change in paypal we must do the condition "if not" sp we can proceed with success checkout, you should see if it changes again later
            amount = request.args.get('totalPrice')
            status = 'Paid'
            user_id = session['user_id']
            item_id= request.args.get('item_id')
            # item_id = request.args.get('item_id')  # Retrieve the item ID from the query parameters
            data = {
                'amount': amount,
                'status': status,
                'user_id': user_id,
                'item_id': item_id
            }
            User.createPayment(data)
            
            flash('Your payment was successful!', 'paymentSuccessful')
            return redirect('/paymentSuccess')
        else:
            print("here is something wrong")
            flash('Something went wrong with your payment', 'paymentNotSuccessful')
            return redirect('/allProducts')
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'paymentNotSuccessful')
        return redirect('/')
    

@app.route('/paymentSuccess')
def payment_success():
    # Send email to the user
    # msg = Message('Purchase Confirmation', recipients=['soncemertiri@gmail.com'])
    # msg.body = 'Thank you for your purchase!'
    # mail.send(msg)
    return render_template('payment_success.html')


# @app.route("/success", methods=["GET"])
# def paymentSuccess():
#     payment_id = request.args.get('paymentId', '')
#     payer_id = request.args.get('PayerID', '')
    
#     try:
#         paypalrestsdk.configure({
#             "mode": "sandbox",
#             "client_id": "AQtIlqp4cJJNLjDFvJQH_4cmmYj-srYBVIP0jjgp5-8wMsCWBYv51HB74GRc5VXo0JijTqEMw3sHy70-",
#             "client_secret": "ELpwmVruy5GUnQHbFr95TC39upzGN0qro4yrXhErp7DYZwOZjgX9LSbZONTFjUz6kVVOBT_KYCpyrvf-"
#         })
        
#         payment = paypalrestsdk.Payment.find(payment_id)
        
#         if not payment.execute({"payer_id": payer_id}):
#             amount = request.args.get('totalPrice')
#             status = 'Paid'
#             user_id = session['user_id']
#             item_id = request.args.get('item_id')
            
#             data = {
#                 'amount': amount,
#                 'status': status,
#                 'user_id': user_id,
#                 'item_id': item_id
#             }
            
#             User.createPayment(data)
            
#             # Send purchase confirmation email
#             send_purchase_confirmation_email()
            
#             flash('Your payment was successful!', 'paymentSuccessful')
#             return redirect('/')
#         else:
#             flash('Something went wrong with your payment', 'paymentNotSuccessful')
#             return redirect('/allProducts')
#     except paypalrestsdk.ResourceNotFound as e:
#         flash('Something went wrong with your payment', 'paymentNotSuccessful')
#         return redirect('/')


# def send_purchase_confirmation_email():
#     # Send email to the user
#     msg = Message('Purchase Confirmation', recipients=['soncemertiri@gmail.com'])
#     msg.body = 'Thank you for your purchase!'
#     mail.send(msg)

@app.route("/cancel", methods=["GET"])
def paymentCancel():
    flash('Payment was canceled', 'paymentCanceled')
    return redirect('/allProducts')