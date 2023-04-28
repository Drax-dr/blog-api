import flask
from flask import request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
db = SQLAlchemy()

app = flask.Flask(__name__,static_folder='static')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
db = SQLAlchemy(app=app)
ma = Marshmallow(app=app)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False, unique=True)
    content = db.Column(db.Text(), nullable=False, unique=True)
    date_posted = db.Column(db.Date, default=datetime.utcnow)
    image = db.Column(db.String(20), nullable=False)

    def __repr__(self) -> str:
        return f"Posts('{self.title}', '{self.content}','{self.image}', '{self.date_posted}')"

class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Posts
        load_instance = True
    fields = ("id", "title", "content", "date_posted", "image")

@app.route("/")
def home():
    all_posts = Posts.query.all()
    data = PostSchema().dump(all_posts, many=True)
    return jsonify(data)

@app.route("/posts/<int:pg_id>")
def get(pg_id):
    pg_id = pg_id
    blog = Posts.query.get(pg_id)
    data = PostSchema().dump(blog)
    return jsonify(data)

@app.route("/add", methods = ['GET','POST'])
def add():
    if request.method == "GET":
        return "<h1>404 Not Found</h1>"
    Post = Posts(
        title = request.form.get("title"),
        content = request.form.get("content"),
        image = request.form.get("image"),
        )
    db.session.add(Post)
    db.session.commit()
    return redirect("/")

@app.route("/delete/<int:pg_id>", methods = ['POST'])
def delete(pg_id):
    pg_id = pg_id
    blog = Posts.query.get(pg_id)
    db.session.delete(blog)
    db.session.commit()
    return redirect("/")

@app.route("/update/<int:pg_id>", methods = ['POST'])
def update(pg_id):
    pg_id = pg_id
    blog = Posts.query.get(pg_id)
    blog.title = request.form.get("title")
    blog.content = request.form.get("content")
    blog.image = request.form.get("image")
    db.session.commit()

    return redirect("/")

if __name__ == "__main__":
    app.run()