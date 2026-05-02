from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "campus-print-secret-2024")
CORS(app)

SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("VITE_SUPABASE_ANON_KEY", "")


@app.route("/")
@app.route("/login")
def login():
    return render_template("auth.html",
                           supabase_url=SUPABASE_URL,
                           supabase_key=SUPABASE_ANON_KEY)


@app.route("/student")
def student():
    return render_template("student.html",
                           supabase_url=SUPABASE_URL,
                           supabase_key=SUPABASE_ANON_KEY)


@app.route("/staff")
def staff():
    return render_template("staff.html",
                           supabase_url=SUPABASE_URL,
                           supabase_key=SUPABASE_ANON_KEY)


@app.route("/api/login", methods=["POST"])
def api_login():
    from supabase import create_client
    body = request.get_json()
    email = body.get("email", "").strip()
    password = body.get("password", "")

    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return jsonify({"error": "Supabase not configured"}), 500

    sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    result = sb.table("campus_users").select("*").eq("email", email).eq("password", password).maybe_single().execute()

    if not result.data:
        return jsonify({"error": "Invalid email or password."}), 401

    return jsonify({"user": result.data})


@app.route("/api/signup", methods=["POST"])
def api_signup():
    from supabase import create_client
    body = request.get_json()
    email = body.get("email", "").strip()
    password = body.get("password", "")
    is_staff = body.get("is_staff", False)

    sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    existing = sb.table("campus_users").select("id").eq("email", email).maybe_single().execute()
    if existing.data:
        return jsonify({"error": "An account with this email already exists."}), 409

    result = sb.table("campus_users").insert({"email": email, "password": password, "is_staff": is_staff}).execute()
    if not result.data:
        return jsonify({"error": "Could not create account."}), 500

    return jsonify({"user": result.data[0]})


@app.route("/api/jobs", methods=["GET"])
def api_get_jobs():
    from supabase import create_client
    sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    user_id = request.args.get("user_id")
    role = request.args.get("role", "student")

    if role == "staff":
        result = sb.table("print_job").select("*, users(email)").order("created_at", desc=True).execute()
    else:
        result = sb.table("print_job").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()

    return jsonify({"jobs": result.data or []})


@app.route("/api/jobs/<job_id>/status", methods=["PATCH"])
def api_update_status(job_id):
    from supabase import create_client
    sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    body = request.get_json()
    status = body.get("status")
    sb.table("print_job").update({"status": status}).eq("id", job_id).execute()
    return jsonify({"ok": True})


@app.route("/api/jobs/<job_id>", methods=["DELETE"])
def api_delete_job(job_id):
    from supabase import create_client
    sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    sb.table("print_job").delete().eq("id", job_id).execute()
    return jsonify({"ok": True})


@app.route("/api/jobs", methods=["POST"])
def api_create_job():
    from supabase import create_client
    sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    body = request.get_json()
    result = sb.table("print_job").insert(body).execute()
    if not result.data:
        return jsonify({"error": "Could not submit job"}), 500
    return jsonify({"job": result.data[0]})


@app.route("/api/storage/sign", methods=["POST"])
def api_sign_upload():
    """Return a signed upload URL from Supabase storage."""
    from supabase import create_client
    sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    body = request.get_json()
    path = body.get("path")
    result = sb.storage.from_("print-files").create_signed_upload_url(path)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
