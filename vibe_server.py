import os
import json
from flask import Flask, send_from_directory, jsonify
from pathlib import Path
from PIL import Image

app = Flask(__name__)
ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = ROOT_DIR / "remote_assets"
THUMBS_DIR = ROOT_DIR / "remote_assets" / "thumbnails"

ASSETS_DIR.mkdir(parents=True, exist_ok=True)
THUMBS_DIR.mkdir(parents=True, exist_ok=True)

def generate_thumbnail(img_path):
    thumb_path = THUMBS_DIR / img_path.relative_to(ASSETS_DIR)
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not thumb_path.exists():
        try:
            with Image.open(img_path) as img:
                img.thumbnail((300, 300))
                img.save(thumb_path, "JPEG")
        except Exception as e:
            print(f"Error thumbnailing {img_path}: {e}")
    return thumb_path

import time
import secrets

# Mock token storage: {token: (path, expiry)}
PRESIGNED_TOKENS = {}

def generate_presigned_url(path):
    token = secrets.token_urlsafe(16)
    expiry = time.time() + 300  # 5 minute expiry
    PRESIGNED_TOKENS[token] = (path, expiry)
    return f"/assets/secure/{token}"

@app.route('/manifest')
def get_manifest():
    manifest = {}
    for img_path in ASSETS_DIR.glob("**/*.*"):
        if img_path.suffix.lower() in [".jpg", ".jpeg", ".png"] and "thumbnails" not in img_path.parts:
            rel_path = img_path.relative_to(ASSETS_DIR)
            parts = rel_path.parts
            if len(parts) >= 3:
                topic, col = parts[0], parts[1]
                if topic not in manifest: manifest[topic] = {}
                if col not in manifest[topic]: manifest[topic][col] = []
                
                generate_thumbnail(img_path)
                
                manifest[topic][col].append({
                    "name": img_path.name,
                    "presigned_url": generate_presigned_url(str(rel_path)),
                    "thumb_url": f"/thumbs/{rel_path}"
                })
    return jsonify(manifest)

@app.route('/assets/secure/<token>')
def serve_secure_asset(token):
    if token not in PRESIGNED_TOKENS:
        return "Invalid Token", 403
    
    path, expiry = PRESIGNED_TOKENS[token]
    if time.time() > expiry:
        del PRESIGNED_TOKENS[token]
        return "Token Expired", 403
    
    # Optional: del PRESIGNED_TOKENS[token] # One-time use? 
    return send_from_directory(ASSETS_DIR, path)

@app.route('/thumbs/<path:path>')
def serve_thumb(path):
    return send_from_directory(THUMBS_DIR, path)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
