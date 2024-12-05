from flask import current_app, session
from flask_app.modules.extensions import DB

voice_query = """
        SELECT
          plan,
          tts_model,
          voice_code,
          CASE language_code
              WHEN 'en-US' THEN 'North American'
              WHEN 'en-AU' THEN 'Australian'
              WHEN 'en-GB' THEN 'British'
              WHEN 'en-IN' THEN 'India'
              ELSE language_code
              END AS language_name,
          language_code,
          gender,
          sample_mp3,
          recommended,
          timestamp
        FROM voices
        WHERE plan = %s
        AND visible = 1
        ORDER BY recommended DESC, sort_order ASC, id ASC
      """


def get_base_voices():
    """Get a list of the base voices available for TTS"""

    q = DB.fetch_all(voice_query, ("base",))
    return q.get("results", [])


def get_premium_voices():
    """Get a list of the premium voices available for TTS"""

    q = DB.fetch_all(voice_query, ("premium",))
    return q.get("results", [])
