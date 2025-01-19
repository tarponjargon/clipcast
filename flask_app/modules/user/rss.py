from flask import Flask, Response, current_app, request
from feedgen.feed import FeedGenerator
from datetime import datetime, date, timezone, timedelta
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import match_uuid
from urllib.parse import urlparse, urlunparse


def serve_rss_feed(userid):
    """Serve the RSS feed for the user, dynamically"""

    if not match_uuid(userid):
        return Response("Invalid user ID", status=400)

    # Initialize the feed
    fg = FeedGenerator()
    fg.load_extension("podcast")

    fg.id(request.url)
    fg.copyright("All rights reserved")
    fg.image(current_app.config.get("DEFAULT_IMAGE"))
    fg.title(f"Your {current_app.config.get('STORE_NAME')} Podcast Feed")
    fg.link(href=current_app.config.get("STORE_URL"), rel="alternate")
    fg.description(current_app.config.get("STORE_META_DESCRIPTION"))
    fg.podcast.itunes_author(current_app.config.get("STORE_NAME"))
    fg.podcast.itunes_block(True)
    fg.language("en")

    # Fetch the latest articles (or data from a live source)
    articles = DB.fetch_all(
        """
        SELECT *
        FROM podcast_content
        WHERE user_id = %s
        AND current_status = 'complete'
        ORDER BY timestamp DESC
        """,
        (userid,),
    )["results"]

    # Add each article to the feed
    for article in articles:
        eastern_timezone = timezone(timedelta(hours=-5))
        article_date = datetime.combine(
            article["article_date"], datetime.min.time()
        ).replace(tzinfo=eastern_timezone)

        article_image_url = article.get("image")
        image = None
        if article_image_url:
            # Parse the URL
            parsed_url = urlparse(article_image_url)

            # Rebuild the URL without the query parameters
            image = urlunparse(parsed_url._replace(query=""))

        fe = fg.add_entry()
        fe.id(article["url"])
        fe.title(article["title"])
        fe.link(href=article["url"])
        fe.description(article["description"])
        fe.pubDate(article_date)
        fe.enclosure(article.get("mp3_url"), article.get("mp3_file_size"), "audio/mpeg")
        fe.podcast.itunes_block(True)
        fe.podcast.itunes_duration(article.get("mp3_duration"))
        try:
            fe.podcast.itunes_image(image)
        except Exception as e:
            fe.podcast.itunes_image(current_app.config.get("DEFAULT_IMAGE"))

    # Generate the RSS feed as an XML string
    rss_feed_data = fg.rss_str(pretty=True).decode("utf-8")

    # Serve the XML as a response with content type 'application/rss+xml'
    return Response(rss_feed_data, mimetype="application/xml")
