from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT)
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        status TEXT)
    ''')

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        conn=sqlite3.connect("tasks.db")
        c=conn.cursor()
        c.execute("INSERT INTO users(username,password) VALUES(?,?)",
                  (username,password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        conn=sqlite3.connect("tasks.db")
        c=conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username,password))

        user=c.fetchone()
        conn.close()

        if user:
            session["user"]=username
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():

    if "user" not in session:
        return redirect("/login")

    conn=sqlite3.connect("tasks.db")
    c=conn.cursor()

    if request.method=="POST":
        task=request.form["task"]
        c.execute(
            "INSERT INTO tasks(task,status) VALUES(?,?)",
            (task,"Pending")
        )
        conn.commit()

    c.execute("SELECT * FROM tasks")
    tasks=c.fetchall()

    conn.close()

    return render_template("dashboard.html",
                           tasks=tasks,
                           user=session["user"])

@app.route("/complete/<int:id>")
def complete(id):

    conn=sqlite3.connect("tasks.db")
    c=conn.cursor()

    c.execute(
        "UPDATE tasks SET status='Completed' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/delete/<int:id>")
def delete(id):

    conn=sqlite3.connect("tasks.db")
    c=conn.cursor()

    c.execute("DELETE FROM tasks WHERE id=?",(id,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True)
