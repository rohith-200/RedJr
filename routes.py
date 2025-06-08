from flask import Flask, render_template, request, send_file, jsonify, make_response, redirect, url_for, Blueprint, session
from app import app, db
from models import ItemImages
from models import User
from models import SavedItems
from sqlalchemy import case, or_
from services.api_items import create_item_with_image, get_recent_items, update_item, delete_item
from services.api_users import register_user, login_user
from services.api_message import send_message, get_inbox_for_user, mark_messages_as_read
from services.api_dashboard import get_dashboard
from services.api_items_sorting_options import sort_items_list as quicksort_items

import io,re

from services.search import searchbp
from models import Items

print("📌 ROUTES.PY LOADED")


def register_blueprints(app):
    app.register_blueprint(searchbp)

@app.route('/')
@app.route('/search')
def home():
    return render_template('search.html')
    

@app.route('/profiles')
def profiles():
    return render_template('profiles.html')

@app.route('/profile/<name>')
def profile(name):
    return render_template(f'{name}.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    success, message = login_user(email, password)

    status_code = 200 if success else 400
    return jsonify({'success': success, 'message': message}), status_code

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/inbox')
def inbox():
    return render_template('inbox.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    success, message = register_user(name, email, password)

    status_code = 200 if success else 400
    return jsonify({'success': success, 'message': message}), status_code

@app.route('/api/item', methods=['POST'])
def create_item():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    success, result = create_item_with_image(session.get('user_id'), request.form, request.files)

    if not success:
        return jsonify({'success': False, 'message': result}), 400

    return jsonify({'success': True, 'message': 'Item posted successfully', 'item_id': result})


@app.route('/api/session')
def session_info():
    user_id = session.get('user_id')
    if user_id:
        return jsonify({'logged_in': True, 'user_id': user_id})
    else:
        return jsonify({'logged_in': False}), 401


@app.route('/api/recent-items', methods=['GET'])
def api_recent_items():
    try:
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify({'success': False, 'message': 'Limit must be an integer'}), 400

    success, result = get_recent_items(limit)

    if not success:
        return jsonify({'success': False, 'message': result}), 500

    return jsonify({'items': result})

@app.route('/api/message', methods=['POST'])
def api_send_message():
    
    sender_id = session.get('user_id')
    if not sender_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    item_id = data.get('item_id')

    success, result = send_message(sender_id, receiver_id, content, item_id)

    if not success:
        return jsonify({'success': False, 'message': result}), 400

    return jsonify({'success': True, 'message': result})


@app.route('/api/inbox', methods=['GET'])
def api_inbox():
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    success, result = get_inbox_for_user(user_id)
    if not success:
        return jsonify({'success': False, 'message': result}), 500

    return jsonify(result)


#@app.route('/api/mark-read', methods=['POST'])
#def api_mark_read():
#    user_id = session.get('user_id')
#    if not user_id:
#        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

@app.route('/api/mark-read', methods=['POST'])
def mark_read():
    data = request.get_json()
    user_id = session.get('user_id')
    sender_id = data.get('sender_id')

    if not sender_id:
        return jsonify({'success': False, 'message': 'Missing sender_id'}), 400

    success, result = mark_messages_as_read(user_id, sender_id)

    if not success:
        return jsonify({'success': False, 'message': result}), 500

    return jsonify({'success': True, 'message': result})

@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))
    else: 
        success, response = get_dashboard(user_id)
        if not success: 
            return jsonify({'success': False, 'message': response}), 404

        return jsonify({
            'selling_listings': response[0],
            'sold_items': response[1],
            'saved_items': response[2]
        }), 200

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    return render_template('email_verification.html')

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    return render_template('dashboard.html', username=user.name)


@app.route('/image/<image_id>')
def image(image_id):
    img = ItemImages.query.filter_by(image_id=int(image_id)).first()

    response = make_response(send_file(
        io.BytesIO(img.image_data),
        mimetype=img.mime_type
    ))

    response.headers['Cache-Control'] = 'public, max-age=86400'

    return response

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = Items.query.get(item_id)
    if not item:
        return "Item not found", 404

    image = ItemImages.query.filter_by(item_id=item_id).first()
    seller = User.query.get(item.seller_id)

    return render_template(
        'item_detail.html',
        item=item,
        image=image,
        seller=seller
    )


@app.route('/contact_seller')
def contact_seller():
    item_title = request.args.get('item', 'Sample Item Title')
    seller_name = request.args.get('seller', 'Tony Hawk')
    price = request.args.get('price', '99.99')
    image_id = request.args.get('image_id')

    image_url = url_for('image', image_id=image_id) if image_id else None

    return render_template(
        'contact_seller.html',
        item={'title': item_title, 'price': price, 'image_url': image_url},
        seller_name=seller_name
    )
@app.route('/new_listing')
def new_listing():
    return render_template('new_listing.html')
@app.route('/message_sent', methods=['GET', 'POST'])
def message_sent():
    return render_template('message_sent.html')
@app.route('/listing_confirmation', methods=['GET', 'POST'])
def listing_confirmation():
    return render_template('listing_confirmation.html')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))  

@app.route('/messages/<int:user_id>/', defaults={'item_id': None})
@app.route('/messages/<int:user_id>/<int:item_id>')
def view_messages(user_id, item_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    current_user_id = session.get('user_id')
    success, inbox_data = get_inbox_for_user(current_user_id)

    if not success:
        return "Error loading inbox", 500

    convo = next(
        (c for c in inbox_data if c["with_user_id"] == user_id and c["item_id"] == item_id),
        None
    )

    if not convo:
        return "Conversation not found", 404

    return render_template(
        'messages.html',
        other_user=convo["with_user_name"],
        messages=convo["messages"],
        item_title=convo["item_title"],
        image_id=convo["image_id"],
        user_id=user_id,
        item_id=item_id
    )
@app.route('/api/save-item', methods=['POST'])
def save_item():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json()
    item_id = data.get('item_id')

    if not item_id:
        return jsonify({'success': False, 'message': 'Missing item ID'}), 400

    # Check if already saved
    existing = SavedItems.query.filter_by(user_id=user_id, item_id=item_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Already saved'}), 409

    new_saved = SavedItems(user_id=user_id, item_id=item_id)
    db.session.add(new_saved)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Item saved'})

@app.route('/api/remove-saved-item', methods=['POST'])
def remove_saved_item():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json()
    item_id = data.get('item_id')

    if not item_id:
        return jsonify({'success': False, 'message': 'Missing item ID'}), 400

    saved = SavedItems.query.filter_by(user_id=user_id, item_id=item_id).first()
    if not saved:
        return jsonify({'success': False, 'message': 'Item not found in saved list'}), 404

    db.session.delete(saved)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Item removed from saved'})

@app.route('/api/mark-sold', methods=['POST'])
def mark_sold():
    data = request.get_json()
    item_id = data.get('item_id')
    user_id = session.get('user_id')

    if not item_id or not user_id:
        return jsonify({'success': False, 'message': 'Invalid request'}), 400

    item = Items.query.filter_by(item_id=item_id, seller_id=user_id).first()
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

    item.is_sold = True
    db.session.commit()

    return jsonify({'success': True})

@app.route('/edit_item/<int:item_id>')
def edit_item(item_id):
    user_id = session.get('user_id')
    item = Items.query.filter_by(item_id=item_id, seller_id=user_id).first()
    if not item:
        return "Item not found or unauthorized", 404

    return render_template('edit_item.html', item=item)


@app.route('/api/approve-item/<int:item_id>', methods=['POST'])
def approve_item(item_id):
    item = Items.query.get(item_id)
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

    item.is_approved = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Item approved'})


@app.route('/api/item/<int:item_id>', methods=['POST'])
def updates_item(item_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

     # Read regular form fields
    title = request.form.get('title')
    description = request.form.get('description')
    price = request.form.get('price')
    category = request.form.get('category')
    
    # Read optional image file
    image = request.files.get('image')

    # Package the data into a dictionary
    data = {
        'title': title,
        'description': description,
        'price': price,
        'category': category,
        'image': image  # Pass this if update_item handles images, or skip if not
    }
    success, message = update_item(item_id, user_id, data)

    if success:
        return redirect(url_for('dashboard'))  # 👈 Redirect to dashboard
    else:
        # Optionally flash an error or redirect back to the form
        return f"Error: {message}", 403



@app.route('/api/item/<int:item_id>', methods=['DELETE'])
def api_delete_item(item_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    success, message = delete_item(item_id, user_id)
    status_code = 200 if success else 403 if message == "Unauthorized" else 404
    return jsonify({'success': success, 'message': message}), status_code

@app.route('/api/sort-items-list', methods=['POST'])
def sort_items_list():
    data = request.get_json()
    sort = data.get('sort')
    items = session.get('items', [])

    option = None
    order_by = None

    if sort == 'price_asc':
        option = 'price'
        order_by = 'ascending'
    elif sort == 'price_desc':
        option = 'price'
        order_by = 'descending'
    elif sort == 'date_desc':
        option = 'created_at'
        order_by = 'descending'

    if items and option and order_by:
        quicksort_items(items, 0, len(items) - 1, option, order_by)

    return jsonify({'items': items})
