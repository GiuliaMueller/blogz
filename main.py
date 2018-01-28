from flask import Flask, request, redirect,render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://blogz:123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key= "ThisIsMySecretKey"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String (120), unique = True)
    password = db.Column(db.String (120))
    blogs = db.relationship('Blog', backref = "owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password
       # self.blogs = blogs

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect ('/login')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user=User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username']=username
            flash('logged in')
            return redirect ('/newpost')
        else:
            flash('username and/or password not valid', 'error')
    return render_template('login.html')

@app.route('/signup', methods=["POST","GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        username_error =True
        
        if " " in username:
            flash("Spaces not permitted")
        elif len(username) <3 or len(username)>20:
            flash("Must be 3 - 20 characters")
        else:
            username_error = False   

        password = request.form["password"]
        password_error = True
        
        if " " in password:
            flash("Spaces not permitted")
        elif len(password) <3 or len(password) >20:
            flash("Must be between 3 and 20 characters")
        else:
            password_error = False
        
        verify = request.form["verify"]
        verify_error = True

        if password != verify:
            flash("Passwords must match")
        else:
            verify_error = False
    #add email code
        
        if  username_error or  verify_error or  password_error:

            return redirect ('/')
        else:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user=User(username,password)
                db.session.add(new_user)
                db.session.commit()
                session['username']=username
                return redirect('/login')
            else:

                flash('that email address previously registered')
            return render_template ("index.html", username = username, username_error = username_error, 
               password_error = password_error, verify_error = verify_error)
        
    return render_template('signup.html')

@app.route("/", methods = ["POST", "GET"])
def index():
    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template("blog.html", blogs = blogs)

@app.route("/blog", methods = ["POST", "GET"])
def blog():
    blogid = request.args.get("id")
    if blogid:
        blog = Blog.query.filter_by(id=blogid).first()
        return render_template("singleblog.html", blog=blog)
    else:
        blogs = Blog.query.order_by(Blog.id.desc()).all()
        return render_template("blog.html", blogs = blogs)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route("/newpost", methods = ["POST", "GET"])
def newpost():
    return render_template("newpost.html")

@app.route("/todos", methods=["POST", "GET"])
def todos():
    title = request.form["title"]
    title_error = ""

    body = request.form["body"]
    body_error = ""

    owner = request.form['owner']
    owner_error = ""
    
    print("body requested")

    if title == "":
        title_error = "Why don't you write something?"
        return render_template("newpost.html", title=title, title_error = title_error)
    if body == "":
        body_error = "Why don't you write something?"
        return render_template("newpost.html", body=body, body_error = body_error)
    elif request.method == "POST":
        blogpost = Blog(title, body, owner)
        db.session.add(blogpost)
 #       db.session.flush()
        db.session.commit()

    idnum = blogpost.id
    return redirect('/blog')
    #return redirect("/blog?id={0}".format(idnum))


if __name__=='__main__':
    app.run()