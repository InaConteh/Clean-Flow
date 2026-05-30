import os
from supabase import create_client, Client
from flask import current_app

def get_supabase_client() -> Client:
    """
    Initializes and returns a Supabase client using configuration from the Flask app.
    """
    url = current_app.config.get("SUPABASE_URL")
    key = current_app.config.get("SUPABASE_KEY")

    if not url or not key:
        # Fallback to environment variables if not in config (useful for scripts outside app context)
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in configuration or environment.")

    return create_client(url, key)
