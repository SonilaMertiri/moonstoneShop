from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.item import Item
from flask_app.models.user import User

# Add the following import for file upload handling
from werkzeug.utils import secure_filename
import os

# Define the upload folder for storing images
UPLOAD_FOLDER = 'flask_app/static/itemsimages'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define allowed extensions for file uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def items():
    items = Item.get_all()
    user = None   # deklarimi me none ketu i userit ben qe edhe kur nuk ka user te loguar te shikohet contenti ne dashbord, nese e heqim jep errore
    if 'user_id' in session:
        data = {
            'id': session['user_id']
        }
        user = User.get_user_by_id(data)
    return render_template('dashboard.html', items=items, user=user)

@app.route('/allProducts')
def all_products():
    items = Item.get_all()
    user = None   # deklarimi me none ketu i userit ben qe edhe kur nuk ka user te loguar te shikohet contenti ne dashbord, nese e heqim jep errore
    if 'user_id' in session:
        data = {
            'id': session['user_id']
        }
        user = User.get_user_by_id(data)
    # Render the allProducts.html template
    return render_template('allProducts.html', items=items, user=user)

@app.route('/about/us')
def about():
    return render_template('about_us.html')

@app.route('/items/new')
def addItem():
    if 'user_id' not in session:
        return redirect('/')
    data={
        'id': session['user_id']
    }
    user=User.get_user_by_id(data)
    # event=Event.get_event_by_id()
    if 'user_id' in session and user['role']=='admin':
        return render_template('addItem.html')
    return redirect('/')


@app.route('/items/new', methods=['POST'])
def addNewItem():
    if 'user_id' not in session:
        return redirect('/')
    data_user = {
        'id': session['user_id']
    }
    user = User.get_user_by_id(data_user)
    if not Item.validate_Item(request.form):
        return redirect(request.referrer)
    if user['role'] == 'admin':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        image = None  # Initialize image variable
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '' and allowed_file(file.filename):
                image = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, image))
        
        data = {
            'name': name,
            'description': description,
            'image': image,  # Use the updated value of 'image'
            'price': price,
            'user_id': session['user_id']
        }
        Item.create(data)
        return redirect('/')
    return redirect('/')



@app.route('/item/<int:id>')
def view_item(id):
    data = {
        'id': id,
        'item_id': id
    }
    item = Item.get_item_by_id(data)
    user = None
    if 'user_id' in session:
        user = User.get_user_by_id({'id': session['user_id']})
    
    return render_template('detailsItem.html', item=item, user=user)



@app.route('/item/edit/<int:id>')
def edit_item(id):
    if 'user_id' not in session:
        return redirect('/')
    data={
        'id':id
    }
    item= Item.get_item_by_id(data)
    if item and item['user_id']== session['user_id']:
        return render_template('editItem.html', item=item)
    return redirect('/')



@app.route('/item/update/<int:id>', methods=['POST'])
def update_item(id):
    if 'user_id' not in session:
        return redirect('/')

    data = {'id': id}
    item = Item.get_item_by_id(data)

    if item and item['user_id'] == session['user_id']:
        if not Item.validate_item_update(request.form):
            return redirect(request.referrer)

        # Handle image upload
        image = item['image']  # Preserve the existing image by default
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '' and allowed_file(file.filename):
                image = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, image))

        # Prepare data for update
        data = {
            'name': request.form['name'],
            'description': request.form['description'],
            'image': image,
            'price': request.form['price'],
            'id': id
        }
        Item.update(data)
        return redirect('/item/' + str(id))

    return redirect('/')



@app.route('/item/delete/<int:id>')
def delete_item(id):
    if 'user_id' not in session:
        return redirect('/')
    data={
        'id': id
    }
    item= Item.get_item_by_id(data)
    if item['user_id']== session['user_id']:
        Item.delete_all_item_comments(data)
        Item.deleteItem(data)
    return redirect('/allProducts')


# routet per comments ose review
@app.route('/comment/new/<int:id>', methods=['POST'])
def add_comment(id):
    data = {
        'id': id
    }
    if 'user_id' not in session:
        return redirect('/')

    comment = request.form['comment']
    if not Item.validate_comment(request.form):
        return redirect(request.referrer)
    item = Item.get_item_by_id(data)
    if not item:
        flash('Invalid item ID', 'error')
        return redirect(request.referrer)
    
    filename = None
    if 'comment_image' in request.files:
        file = request.files['comment_image']
        if file.filename != '' and allowed_file(file.filename):
            comment_image = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], comment_image))
        else:
            flash('Invalid file format', 'error')
            return redirect(request.referrer)
    
    data1 = {
        'comment': comment,
        'comment_image': comment_image,
        'item_id': id,
        'user_id': session['user_id']
    }
    
    Item.create_comment(data1)
    
    flash('Action added successfully!', 'success')
    return redirect('/')


# @app.route('/action/edit/<int:id>')
# def edit_action(id):
#     if 'user_id' not in session:
#         return redirect('/')

#     data = {
#         'id': id
#         }
#     action = Event.get_action_by_id(data)

#     if action and action['user_id'] == session['user_id']:
#         event_data = {
#             'id': action['event_id']
#             }
#         event = Event.get_event_by_id(event_data)

#         return render_template('editAction.html', action=action, event=event)
    
#     return redirect(request.referrer)


# @app.route('/action/edit/<int:id>', methods=['POST'])
# def update_action(id):
#     if 'user_id' not in session:
#         return redirect('/')

#     title = request.form.get('title')
#     content = request.form.get('content')
#     image = request.files['image'] if 'image' in request.files else None

#     filename = None
#     if image and allowed_file(image.filename):
#         filename = secure_filename(image.filename)
#         image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#     else:
#         flash('Invalid file format', 'error')
#         return redirect('/item/new/{}'.format(id))

#     data = {
#         'id': id,
#         'title': title,
#         'content': content,
#         'image': filename  
#     }

#     updated = Event.update_action(data)

#     if updated:
#         return redirect('/event')  
#     else:
#         flash('Failed to update action', 'error')
#         return redirect(request.referrer)
    


@app.route('/delete/comment/<int:id>')
def delete_comment(id):
    if 'user_id' not in session:
        return redirect('/')
    data={
        'id':id
    }
    comment=Item.get_comment_by_id(data)
    if comment['user_id']== session['user_id']:
        Item.delete_comment(data)
    return redirect(request.referrer)


# @app.route('/best/seller')
# def best_selling_items():
#     items = Item.best_seller()
#     return render_template('best_selling_items.html', items=items)

@app.route('/best/seller')
def best_selling_items():
    # Call the class method to retrieve best selling items
    best_seller = Item.best_seller()
    user = None   # deklarimi me none ketu i userit ben qe edhe kur nuk ka user te loguar te shikohet contenti ne dashbord, nese e heqim jep errore
    if 'user_id' in session:
        data = {
            'id': session['user_id']
        }
        user = User.get_user_by_id(data)

    # Render the HTML template with the retrieved items
    return render_template('best_seller.html', items=best_seller, user=user)
