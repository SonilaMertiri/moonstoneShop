from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.message import Message
from flask_app.models.user import User


@app.route('/new/message')
def new_message():
    if 'user_id' not in session:
        return redirect('/')
    data = {
            'id': session['user_id']
        }
    user = User.get_user_by_id(data)
    return render_template('newMessage.html', user=user)

@app.route('/message/submit', methods=['POST'])
def sent_message():
    if 'user_id' not in session:
        return redirect('/')
    if not Message.validate_message(request.form):
        return redirect(request.referrer)
    data={
            'full_name': request.form['full_name'],
            'message': request.form['message'],
            'user_id': session['user_id']
        }
    Message.create_message(data)
    return redirect('/allMessages')


@app.route('/allMessages')
def all_messages():
    messages = Message.get_all()
    # user = None   # deklarimi me none ketu i userit ben qe edhe kur nuk ka user te loguar te shikohet contenti ne dashbord, nese e heqim jep errore
    if 'user_id' in session:
        data = {
            'id': session['user_id']
        }
        user = User.get_user_by_id(data)
    # Render the allProducts.html template
    return render_template('allMessages.html', messages=messages, user=user)