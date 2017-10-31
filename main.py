from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'sdfgty6789iokujhy'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__ (self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username 
        self.password = password 

@app.before_request
def require_login():
    allowed_routes = ['login', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        #if user:
        #    user = User.query.first()
        if user and user.password == password:
            session['user'] = username
            flash("Logged in")
            return redirect('/blog') 
        else:
            flash('Username or password incorrect', 'error')
            return redirect('/blog')
    
    if request.method == 'GET':
        return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username'] 
        password = request.form['password']
        verify = request.form['verify']
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count>0:
            flash('Username already taken', 'error')
            return redirect('/signup')
        if password != verify:
            flash('Passwords did not match', 'error')
            return redirect('/signup')
   
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            existing_user = User.query.first()
            flash('user already exists', 'error')
            return redirect('/signup')
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return render_template('blog.html')
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['user']
    return render_template('blog.html')


@app.route('/newpost', methods = ['POST', 'GET']) 
def blog():
    if request.method == 'POST':
        

        blog_title = request.form['title']
        blog_body = request.form['body']
        
        # blog = Blog(blog_title, blog_body)
        blog_title_error = ""
        blog_body_error = "" 
        owner = User.query.filter_by(username=session['user']).first()

        if len(blog_title)>120:
            blog_title_error = "Title too long"
            
        if len(blog_body)>1000:
            blog_body_error = "Body too long"
            
        if len(blog_title) <=0:
            blog_title_error = "Title can't be empty"
           
        if len(blog_body) <=0:
            blog_body_error = "Body can't be empty"
              
        if not blog_title_error and not blog_body_error: 
            #owner_id = User.query.filter_by(id).first()
            blog1 = Blog(blog_title, blog_body, owner)
            db.session.add(blog1)
            db.session.commit()
            
            blog = Blog.query.order_by('-id').first()
            query_parm_url = '/blog?id=' + str(blog.id)
            return redirect(query_parm_url)
        else:
            return render_template('newpost.html', blog_title_error=blog_title_error, blog_body_error=blog_body_error)
    if request.method == 'GET':
        return render_template('newpost.html')

@app.route('/blog', methods=['GET'])
def index():
    if request.args.get("id"):
        blogger = Blog.query.filter_by(id = request.args.get("id")).first()
        return render_template('singleUser.html', blogger=blogger)

    if request.args.get("user"):
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        blogs = Blog.query.filter_by(owner=user).all()
        return render_template('newtemplate.html', blogs=blogs)

    else:    
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)            


if  __name__=='__main__':
    app.run()


