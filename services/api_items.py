from app import db
from sqlalchemy import desc 
from models import Items, ItemImages
from PIL import Image
import io

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_CONDITIONS = {
    'Brand New', 'Used - Like New', 'Used - Good', 'Used - Acceptable'
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Creating new Item
def create_item_with_image(user_id, form, files):
    try:
        # Validate required fields
        title = form.get('title')
        description = form.get('description')
        category_id = form.get('category_id')
        price = form.get('price')
        condition = form.get('condition')
        images = files.getlist('image')

        if not all([title, description, category_id, price, condition]):
            return False, 'Missing required fields'

        if condition not in ALLOWED_CONDITIONS:
            return False, 'Invalid item condition'

        if len(images) != 1:
            return False, 'Exactly one image must be uploaded'

        image_file = images[0]

        if not allowed_file(image_file.filename):
            return False, 'Invalid image format'

        # Resize and prepare image
        try:
            image = Image.open(image_file.stream)
            image.thumbnail((300, 300))
            byte_io = io.BytesIO()
            image_format = 'JPEG' if image.mode in ['RGB', 'L'] else 'PNG'
            image.save(byte_io, format=image_format)
            image_data = byte_io.getvalue()
        except Exception as img_err:
            return False, f'Image processing failed: {str(img_err)}'

        # Create item
        item = Items(
            title=title,
            item_description=description,
            category_id=category_id,
            price=price,
            item_condition=condition,
            seller_id=user_id,
            is_approved=False
        )
        db.session.add(item)
        db.session.commit()

        # Attach image
        img = ItemImages(
            item_id=item.item_id,
            image_data=image_data,
            mime_type=image_file.mimetype
        )
        db.session.add(img)
        db.session.commit()

        return True, item.item_id

    except Exception as e:
        return False, f'Item creation failed: {str(e)}'


def get_recent_items(limit=10):
    try:
        items = Items.query.filter_by(is_sold=False, is_approved=True).order_by(desc(Items.created_at)).limit(limit).all()
        results = []

        for item in items:
            first_image = ItemImages.query.filter_by(item_id=item.item_id).first()
            image_id = first_image.image_id if first_image else None

            results.append({
                "item_id": item.item_id,
                "title": item.title,
                "price": float(item.price),
                "condition": item.item_condition,
                "created_at": item.created_at.isoformat(),
                "image_id": image_id
            })

        return True, results

    except Exception as e:
        return False, str(e)


def update_item(item_id, user_id, data):
    try:
        item = Items.query.get(item_id)
        if not item:
            return False, "Item not found"
        if item.seller_id != user_id:
            return False, "Unauthorized"

        item.title = data.get('title', item.title)
        item.item_description = data.get('description', item.item_description)
        item.price = data.get('price', item.price)
        item.item_condition = data.get('condition', item.item_condition)
        item.category_id = data.get('category_id', item.category_id)

        db.session.commit()
        return True, "Item updated successfully"

    except Exception as e:
        return False, f"Update failed: {str(e)}"


def delete_item(item_id, user_id):
    try:
        item = Items.query.get(item_id)
        if not item:
            return False, "Item not found"
        if item.seller_id != user_id:
            return False, "Unauthorized"

        db.session.delete(item)
        db.session.commit()
        return True, "Item deleted successfully"

    except Exception as e:
        return False, f"Delete failed: {str(e)}"


