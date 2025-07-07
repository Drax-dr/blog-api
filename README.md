# Flask Blog API
This is a simple blog API built with Flask, SQLite, SQLAlchemy, and Flask-Admin. It supports admin authentication, image uploads, and a JSON-based API to fetch blog posts.
## Features
- Admin login and authentication using Flask-Login
- Secure password hashing with Werkzeug
- Image uploads saved to a local folder
- RESTful API using Flask-Marshmallow
- Admin dashboard powered by Flask-Admin
- SQLite database wiath two separate binds: one for posts, one for admin users
## How to Run
### 1. Clone the repository
```bash
git clone https://github.com/your-username/blog-api.git
cd blog-api
```
## Create Virtual Environment
```bash
python -m venv venv
```
### Windows
```bash
venv\Scripts\activate
```
### macOS/Linux
```bash
source venv/bin/activate
```
### Install Requirements
```bash
pip install -r requirements.txt
```
## Inside Python shell
```python
from app import db
db.create_all()
db.create_all(bind='Admin')
exit()
```
## Run 
```bash
python app.py
```
