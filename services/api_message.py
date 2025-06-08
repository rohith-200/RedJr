from app import db
from sqlalchemy import or_
from datetime import datetime
from models import Message, User, Items, ItemImages

def send_message(sender_id, receiver_id, content, item_id=None):
    try:
        if not all([receiver_id, content]):
            return False, 'Missing required fields'

        msg = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            item_id=item_id,
            timestamp=datetime.utcnow(),
            is_read=False
        )

        db.session.add(msg)
        db.session.commit()

        return True, 'Message sent successfully'
    except Exception as e:
        return False, str(e)


def get_inbox_for_user(user_id):
    try:
        # Get all messages involving the user
        messages = Message.query.filter(
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        ).order_by(Message.timestamp.asc()).all()

        conversation_map = {}

        for msg in messages:
            other_user_id = msg.receiver_id if msg.sender_id == user_id else msg.sender_id
            convo_key = other_user_id

            if convo_key not in conversation_map:
                conversation_map[convo_key] = {
                    "with_user_id": other_user_id,
                    "messages": []
                }

            conversation_map[convo_key]["messages"].append({
                "from": msg.sender_id,
                "to": msg.receiver_id,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "is_read": msg.is_read,
                "item_id": msg.item_id  # Save for optional display
            })

        results = []
        for other_user_id, convo in conversation_map.items():
            other_user = User.query.get(other_user_id)
            messages = convo["messages"]
            latest_msg = messages[-1]

            # Optionally show one item's info (most recent)
            item_id = latest_msg.get("item_id")
            item = Items.query.get(item_id) if item_id else None
            first_image = ItemImages.query.filter_by(item_id=item_id).first() if item_id else None
            image_id = first_image.image_id if first_image else None

            results.append({
                "with_user_id": other_user.id,
                "with_user_name": other_user.name,
                "item_id": item.item_id if item else None,
                "item_title": item.title if item else None,
                "image_id": image_id,
                "messages": messages
            })

        return True, results

    except Exception as e:
        return False, str(e)


def mark_messages_as_read(current_user_id, sender_id):
    try:
        messages = Message.query.filter_by(
            sender_id=sender_id,
            receiver_id=current_user_id,
            is_read=False
        ).all()

        for msg in messages:
            msg.is_read = True

        db.session.commit()
        return True, f'{len(messages)} message(s) marked as read'
    except Exception as e:
        return False, str(e)