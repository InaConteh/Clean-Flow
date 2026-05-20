from flask import jsonify, request

from app.routes import api_bp
from app.extensions import limiter
from app.services.sms_handler import SMSHandler


@api_bp.route("/sms/callback", methods=["POST"])
@limiter.limit("30 per minute")
def sms_callback():
    """Africa's Talking inbound SMS webhook."""
    payload = request.get_json(silent=True) or request.form.to_dict()
    from_number = payload.get("from") or payload.get("phoneNumber", "")
    text = payload.get("text") or payload.get("message", "")

    reply = SMSHandler().handle(from_number, text)
    return jsonify({"response": reply})
