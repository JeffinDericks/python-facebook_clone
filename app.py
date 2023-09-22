from flask import Flask, request, render_template, redirect, session, url_for
from pymongo import MongoClient
import sqlite3 as sql


app = Flask(__name__)
app.secret_key = "jef123"


client = MongoClient('mongodb://localhost:27017')
db = client.db
doc = db.doc

def isloggedin():
    return "username" in session

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        doc.insert_one({'username': email, 'password': password})
        return redirect (url_for('login'))

    return render_template('signup.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = doc.find_one({'username': email, 'password': password})
        if user:
            session['username'] = email
            return redirect(url_for('facebook'))

        return 'Login failed. Please check your credentials.'

    return render_template('login.html')

@app.route('/logout', methods = ["GET","POST"])
def logout():
    if request.method == "POST":
        print(session)
        session.pop('username',None)
        print(session)
        return redirect(url_for('login'))
    return redirect(url_for('login'))
    

@app.route('/facebook')
def facebook():
    if isloggedin:
        con = sql.connect("user.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("select * from post")
        fet = cur.fetchall()
        count = db.count.find_one()  

        count1 = int(count.get('count1'))
        count2 = int(count.get('count2'))
        count3 = int(count.get('count3'))

        return render_template("facebook.html", count1=count1, count2=count2, count3=count3, post = fet)
    
    else:
        return "not able to access"


@app.route('/operate/<counter>', methods=["GET", "POST"])
def increment(counter):
    if request.method == "POST":
        count = db.count.find_one()
        count1 = int(count.get('count1'))
        count2 = int(count.get('count2'))
        count3 = int(count.get('count3'))

        if counter == '1':
            count1 += 1
        elif counter == '2':
            count2 += 1
        elif counter == '3':
            count3 += 1

        db.count.update_one({}, {"$set": {"count1": count1, "count2": count2, "count3": count3}})
    return redirect(url_for('facebook'))

@app.route('/post', methods = ["GET","POST"])
def post():
    if request.method == "GET":
        return render_template ("post.html")
    if request.method == "POST":
        file = request.files["file"]
        file_exten = ["jpg","jpeg","png","gif"]
        upload_file_exten = file.filename.split(".")[1]
        if upload_file_exten in file_exten:
            path = f"static/uploads/{file.filename}"
            file.save(path)
            try:
                conn = sql.connect("user.db")
                cursor = conn.cursor()
                cursor.execute("""insert into post values(:userid,:username,
                            :imagelink)""",{'userid':1,'username':'__d_rex__','imagelink':path})
                conn.commit()
                conn.close()
            except:
                return render_template('post.html')
        else:
            return render_template('post.html') 
        return redirect(url_for("facebook"))


            


            



if __name__ == '__main__':
    app.run(debug=True)
