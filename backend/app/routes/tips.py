from flask import jsonify

from app.routes import api_bp

TIPS = [
    {
        "id": 1,
        "title": "Safe Water",
        "body": "Green sources are safe to drink. Always use a clean container.",
        "icon": "water-drop",
    },
    {
        "id": 2,
        "title": "Yellow / Caution",
        "body": "Boil water for at least 1 minute before drinking.",
        "icon": "warning",
    },
    {
        "id": 3,
        "title": "Report Issues",
        "body": "Text CAUSE <ID> <CODE> via SMS or use the web form to report problems.",
        "icon": "wrench",
    },
    {
        "id": 4,
        "title": "Drought",
        "body": "Conserve water during dry seasons. Check STATUS for your nearest source.",
        "icon": "sun",
    },
]


@api_bp.route("/tips", methods=["GET"])
def get_tips():
    return jsonify({"tips": TIPS})
