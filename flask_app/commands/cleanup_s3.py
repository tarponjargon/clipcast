import click
from flask import current_app
from flask.cli import with_appcontext
from datetime import datetime, timedelta, timezone
import boto3
from flask_app.modules.extensions import DB


@current_app.cli.command("delete_old_files")
@with_appcontext
def delete_old_files():
    """Delete files older than 90 days from R2."""
    s3 = boto3.client(
        "s3",
        endpoint_url=current_app.config.get("S3_URL"),
        aws_access_key_id=current_app.config.get("S3_ACCESS_KEY"),
        aws_secret_access_key=current_app.config.get("S3_SECRET_ACCESS_KEY"),
    )
    bucket_name = current_app.config.get("S3_BUCKET")
    retention_period = timedelta(days=current_app.config.get("EPISODE_RETENTION_DAYS"))
    now = datetime.now(timezone.utc)

    response = s3.list_objects_v2(Bucket=bucket_name)
    if "Contents" in response:
        for obj in response["Contents"]:
            if now - obj["LastModified"] > retention_period:
                s3.delete_object(Bucket=bucket_name, Key=obj["Key"])
                print(f"Deleted {obj['Key']}")

                # delete from the database
                episode_url = current_app.config.get("S3_PUBLIC_URL") + obj["Key"]
                DB.delete_query(
                    """DELETE FROM podcast_content WHERE mp3_url = %s""", (episode_url)
                )
