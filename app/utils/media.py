import os
import cloudinary
import cloudinary.uploader
from flask import current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Media


def configure_cloudinary():
    cloud_name = current_app.config.get("CLOUDINARY_CLOUD_NAME")
    api_key = current_app.config.get("CLOUDINARY_API_KEY")
    api_secret = current_app.config.get("CLOUDINARY_API_SECRET")
    if cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )
        return True
    return False


def allowed_file(filename, allowed_set=None):
    if allowed_set is None:
        allowed_set = current_app.config.get("ALLOWED_EXTENSIONS", set())
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_set
    )


def upload_to_cloudinary(file, folder="bamstudio", resource_type="auto"):
    """Upload file to Cloudinary. Returns result dict or None."""
    if not configure_cloudinary():
        # Fallback: local storage for development without Cloudinary
        return _local_upload(file, folder)

    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type=resource_type,
            use_filename=True,
            unique_filename=True,
        )
        return result
    except Exception as e:
        current_app.logger.error(f"Cloudinary upload error: {e}")
        return None


def _local_upload(file, folder="bamstudio"):
    """Development fallback when Cloudinary is not configured."""
    from flask import url_for
    import uuid

    upload_dir = os.path.join(current_app.root_path, "static", "uploads", folder)
    os.makedirs(upload_dir, exist_ok=True)
    original = secure_filename(file.filename)
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else "bin"
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(upload_dir, filename)
    file.save(path)
    url = f"/static/uploads/{folder}/{filename}"
    return {
        "secure_url": url,
        "public_id": f"{folder}/{filename}",
        "format": ext,
        "resource_type": "image" if ext in ("jpg", "jpeg", "png", "webp", "gif") else "raw",
        "bytes": os.path.getsize(path),
        "width": None,
        "height": None,
    }


def save_media_record(upload_result, original_filename, uploaded_by=None, alt_text=None, folder="bamstudio"):
    if not upload_result:
        return None
    media = Media(
        filename=upload_result.get("public_id", "").split("/")[-1],
        original_filename=original_filename,
        url=upload_result.get("secure_url") or upload_result.get("url"),
        public_id=upload_result.get("public_id"),
        resource_type=upload_result.get("resource_type", "image"),
        format=upload_result.get("format"),
        size_bytes=upload_result.get("bytes"),
        width=upload_result.get("width"),
        height=upload_result.get("height"),
        alt_text=alt_text,
        folder=folder,
        uploaded_by=uploaded_by,
    )
    db.session.add(media)
    db.session.commit()
    return media


def delete_from_cloudinary(public_id, resource_type="image"):
    if not configure_cloudinary():
        return False
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return True
    except Exception as e:
        current_app.logger.error(f"Cloudinary delete error: {e}")
        return False
