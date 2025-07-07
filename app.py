import os, base64
from datetime import datetime

from flask import Flask, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_required, UserMixin, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Flask app setup
app = Flask(__name__, static_folder='static')
app.config["SECRET_KEY"] = 'abcdefghijklmnopqrstuvwxyz'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.config["SQLALCHEMY_BINDS"] = {
    "Admin": "sqlite:///admin.db"
}
app.config['UPLOAD_FOLDER'] = './static/images'

# Extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
login_manager = LoginManager(app)
admin_panel = Admin(app)

# Models
class Admin(db.Model, UserMixin):
    __bind_key__ = 'Admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    _password = db.Column("password", db.Text, nullable=False)
    date_joined = db.Column(db.Date, default=datetime.utcnow)
    image = db.Column(db.String(120))
    about = db.Column(db.Text, nullable=False, unique=True)

    def set_password(self, password):
        self._password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password, password)

    def __repr__(self):
        return f"<Admin {self.username}>"

admin_panel.add_view(ModelView(Admin, db.session, endpoint="admins_"))

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False, unique=True)
    date_posted = db.Column(db.Date, default=datetime.utcnow)
    image = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(20), nullable=False, unique=True)

    def __repr__(self):
        return f"Posts('{self.title}', '{self.slug}')"

admin_panel.add_view(ModelView(Posts, db.session, endpoint="posts_"))

# Schema
class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Posts
        load_instance = True
    fields = ("id", "title", "content", "date_posted", "image")

# Login
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(user_id)

# Routes
@app.route("/")
def home():
    all_posts = Posts.query.all()
    data = PostSchema(many=True).dump(all_posts)
    return jsonify(data)

@app.route("/p/<slug>")
def get_by_slug(slug):
    blog = Posts.query.filter_by(slug=slug).first_or_404()
    data = PostSchema().dump(blog)
    return jsonify(data)

@app.route("/posts/<int:pg_id>")
def get(pg_id):
    blog = Posts.query.get_or_404(pg_id)
    data = PostSchema().dump(blog)
    return jsonify(data)

@app.route("/cur", methods=['GET'])
@login_required
def cur():
    return f"YOU ARE {current_user.username}"

@app.route("/add", methods=['POST'])
@login_required
def add():
    image = request.files['image']
    path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(path)
    slug = base64.urlsafe_b64encode(os.urandom(6)).decode('utf-8').rstrip('=')

    post = Posts(
        title=request.form["title"],
        content=request.form["content"],
        image=path,
        slug=slug
    )
    db.session.add(post)
    db.session.commit()
    return redirect("/")

@app.route("/delete/<int:pg_id>", methods=['POST'])
@login_required
def delete(pg_id):
    blog = Posts.query.get_or_404(pg_id)
    db.session.delete(blog)
    db.session.commit()
    return redirect("/")

@app.route("/update/<int:pg_id>", methods=['POST'])
@login_required
def update(pg_id):
    blog = Posts.query.get_or_404(pg_id)
    blog.title = request.form["title"]
    blog.content = request.form["content"]
    blog.image = request.form["image"]
    db.session.commit()
    return redirect("/")

@app.route("/admin_login", methods=["POST"])
def get_admin():
    form = request.form
    username = form.get("username")
    password = form.get("password")

    admin = Admin.query.filter_by(username=username).first()
    if admin and admin.verify_password(password):
        login_user(admin)
        return jsonify({'message': 'You are Logged in'})
    return jsonify({'Error': 'Invalid username or password'})

# Main
if __name__ == "__main__":
    app.run(debug=True)
