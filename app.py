import os, base64
import flask
from werkzeug.security import generate_password_hash,check_password_hash
from flask import request, redirect, jsonify
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_required, UserMixin, login_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
app = flask.Flask(__name__,static_folder='static')
app.config["SECRET_KEY"] = 'abcdefghijklmnopqrstuvwxyz'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.config["SQLALCHEMY_BINDS"] = {
    "Admin":"sqlite:///admin.db"
}
app.config['UPLOAD_FOLDER'] = './static/images'
login_manager.init_app(app=app)
db = SQLAlchemy(app=app)
ma = Marshmallow(app=app)
admin_user = Admin(app=app)

class Admin(db.Model, UserMixin):
    __bind_key__ = 'Admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text(), nullable=False, unique=True)
    date_joined = db.Column(db.Date, default=datetime.utcnow)
    image = db.Column(db.String(120))
    about = db.Column(db.Text, nullable=False, unique=True)

    @property
    def password(self):
        return AttributeError("Password is n0t a readable format!")
    
    @password.setter
    def password(self,password):
        self.password = generate_password_hash(password)

    def verify_password(self,password):
        print(password)
        return check_password_hash(str(self.password), str(password))
    
    def __repr__(self):
        return "<User %s>" % self.username

admin_user.add_view(ModelView(Admin,db.session,endpoint="admins_"))

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False, unique=True)
    content = db.Column(db.Text(), nullable=False, unique=True)
    date_posted = db.Column(db.Date, default=datetime.utcnow)
    image = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(20), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"Posts('{self.title}', '{self.content}','{self.image}', '{self.date_posted}')"

admin_user.add_view(ModelView(Posts,db.session,endpoint="posts_"))

class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Posts
        load_instance = True
    fields = ("id", "title", "content", "date_posted", "image")

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(user_id)

@app.route("/")
def home():
    all_posts = Posts.query.all()
    data = PostSchema().dump(all_posts, many=True)
    return jsonify(data)

@app.route("/p/<slug>")
def get_by_slug(slug):
    slug = slug
    blog = db.session.query(Posts).filter_by(slug=slug).first()
    data = PostSchema().dump(blog)
    return jsonify(data)

@app.route("/posts/<int:pg_id>")
def get(pg_id):
    pg_id = pg_id
    blog = Posts.query.get(pg_id)
    data = PostSchema().dump(blog)
    return jsonify(data)

@app.route("/cur", methods = ['GET','POST'])
@login_required
def cur():
    return "YOU ARE "+current_user.username

@app.route("/add", methods = ['GET','POST'])
@login_required
def add():
    if request.method == "GET":
        return "<h1>404 Not Found</h1>"
    id = base64.b64encode(os.urandom(32))[:10].decode('utf-8')
    slug = id.replace('/','')
    image = request.files['image']
    path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(path)
    print(path)
    Post = Posts(
        title = request.form["title"],
        content = request.form["content"],
        image = path,
        slug = slug,
        )
    db.session.add(Post)
    db.session.commit()
    return redirect("/")

@app.route("/delete/<int:pg_id>", methods = ['POST'])
@login_required
def delete(pg_id):
    pg_id = pg_id
    blog = Posts.query.get(pg_id)
    db.session.delete(blog)
    db.session.commit()
    return redirect("/")

@app.route("/update/<int:pg_id>", methods = ['POST'])
@login_required
def update(pg_id):
    pg_id = pg_id
    blog = Posts.query.get(pg_id)
    blog.title = request.form.get("title")
    blog.content = request.form.get("content")
    blog.image = request.form.get("image")
    db.session.commit()

    return redirect("/")

@app.route("/admin_login", methods=["POST"])
def get_admin():
    form = request.form
    user = form["username"]
    passwd = form["password"]
    print(user,passwd)
    admin = db.session.query(Admin).filter_by(username=user).first()
    print(admin)
    if admin:
        if check_password_hash(str(admin.password), str(passwd)):
            login_user(admin)
            res = jsonify({'message':'You are Logged in'})
        else:
            res = jsonify({'Error':'Invalid password'})
    else:
        res = jsonify({'Error':'You are not admin'})
    return res

if __name__ == "__main__":
    app.run()