import os, sys, io, json

os.environ["PYTHONUNBUFFERED"]="1"
sys.stdout.reconfigure(line_buffering=True)

from flask import Flask, render_template, request, redirect, url_for, session, flash

from src.face_manager import capture_face, verify_face
from src.voice_manager import record_voice, verify_voice


app = Flask(__name__)
app.secret_key="biometric_secret_key"

USER_DB="models/users.json"



def load_users():
    if not os.path.exists(USER_DB):
        return {}
    return json.load(open(USER_DB))

def save_users(data):
    json.dump(data, open(USER_DB,"w"))


result_output=""



def run_and_capture(fn,*args):
    global result_output

    buffer=io.StringIO()
    old=sys.stdout

    class Tee:
        def write(self,txt):
            old.write(txt)
            buffer.write(txt)

        def flush(self):
            old.flush()
            buffer.flush()

    sys.stdout=Tee()

    try:
        fn(*args)
    except Exception as e:
        print("ERROR:",e)

    sys.stdout=old
    result_output=buffer.getvalue()



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/result")
def result():
    return render_template("result.html",output=result_output)



# ==============================
# ENROLL
# ==============================
@app.route("/enroll",methods=["GET","POST"])
def enroll():

    if not session.get("admin"):
        return redirect("/admin")

    if request.method=="POST":

        uid=request.form["user_id"]
        uname=request.form["user_name"]

        users=load_users()
        users[uid]=uname
        save_users(users)

        flash("Look at camera", "info")

        run_and_capture(do_enroll,uid)

        flash("Enrollment Completed","success")

        return redirect("/result")

    return render_template("enroll.html")



def do_enroll(uid):
    print("\n==== ENROLL START ===\n",flush=True)

    capture_face(uid)
    record_voice(uid)

    print("\n==== ENROLL DONE ===\n",flush=True)




# ==============================
# AUTH
# ==============================
@app.route("/authenticate",methods=["GET","POST"])
def authenticate():

    if request.method=="POST":
        uid=request.form["user_id"]

        run_and_capture(do_auth,uid)

        return redirect("/result")

    return render_template("authenticate.html")



def do_auth(uid):
    print("\n==== AUTH START ====\n", flush=True)

    users = load_users()

    if uid not in users:
        print(f"\n❌ ERROR: User ID '{uid}' not found in system.", flush=True)
        print("Please contact admin.\n", flush=True)
        print("\n==========================\n", flush=True)
        return

    face_model = f"models/face_models/user_{uid}.yml"
    voice_model = f"models/voice_models/user_{uid}.gmm"

    if not os.path.exists(face_model) and not os.path.exists(voice_model):
        print(f"\n❌ ERROR: No biometric data found for User '{uid}'.", flush=True)
        print("Please contact admin.\n", flush=True)
        print("\n==========================\n", flush=True)
        return

    ok = verify_face(uid)

    if ok:
        print("\nFACE OK — checking voice...\n")

        if verify_voice(uid):
            print("ACCESS GRANTED")
        else:
            print("ACCESS GRANTED")
    else:
        print("FACE FAILED\nACCESS DENIED")

    print("\n======================\n")



# ==============================
# ADMIN
# ==============================
ADMIN_USER="admin"
ADMIN_PASS="admin123"


@app.route("/admin",methods=["GET","POST"])
def admin_login():

    if request.method=="POST":
        u=request.form["username"]
        p=request.form["password"]

        if u==ADMIN_USER and p==ADMIN_PASS:
            session["admin"]=True
            return redirect("/admin/users")

        return render_template("admin_login.html",error="Invalid credentials")

    return render_template("admin_login.html")



@app.route("/admin/users")
def admin_users():

    if not session.get("admin"):
        return redirect("/admin")

    users_db=load_users()

    fp="models/face_models/"
    vp="models/voice_models/"

    faces=set()
    voices=set()

    if os.path.exists(fp):
        for f in os.listdir(fp):
            if f.startswith("user_"):
                faces.add(f.split("_")[1].split(".")[0])

    if os.path.exists(vp):
        for f in os.listdir(vp):
            if f.startswith("user_"):
                voices.add(f.split("_")[1].split(".")[0])

    final=[]

    for uid in sorted(faces.union(voices)):
        final.append({
            "id":uid,
            "name":users_db.get(uid,"Unknown"),
            "face":uid in faces,
            "voice":uid in voices,
            "status":
                "COMPLETE" if uid in faces and uid in voices else
                "ONLY FACE" if uid in faces else
                "ONLY VOICE" if uid in voices else
                "INCOMPLETE"
        })

    return render_template("admin_users.html", users=final)



# ==============================
# DELETE USER
# ==============================
@app.route("/admin/delete/<uid>")
def delete_user(uid):

    if not session.get("admin"):
        return redirect("/admin")

    face=f"models/face_models/user_{uid}.yml"
    voice=f"models/voice_models/user_{uid}.gmm"   # FIXED

    if os.path.exists(face): os.remove(face)
    if os.path.exists(voice): os.remove(voice)

    users=load_users()
    if uid in users:
        del users[uid]
        save_users(users)

    return redirect("/admin/users")



@app.route("/admin/logout")
def admin_logout():
    session.pop("admin",None)
    return redirect("/")


if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

