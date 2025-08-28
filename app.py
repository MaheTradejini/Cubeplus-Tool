from flask import Flask, flash, redirect, render_template, url_for, session
from forms import RegisterForm, LoginForm
from models import db, User
from flask_bcrypt import Bcrypt
# import psycopg2


# conn = psycopg2.connect(
#     host="localhost",
#     database="restapi",
#     user="postgres",
#     password="admin123"
# )


def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = "APPSECRECTKEY"
  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost:5432/flask_db'
  bcrypt = Bcrypt()

  db.init_app(app)
  bcrypt.init_app(app)

  with app.app_context():
    db.create_all()

  @app.route("/")
  def index():
    return render_template("home.html")


  @app.route("/login")
  def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.name
            flash('You have been logged in!', 'success')
    return render_template("login.html", form=form)





  @app.route("/register", methods = ['GET', 'POST'])
  def login():
    form = RegisterForm()
    if form.validate_on_submit():
        hased_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hased_password,
        )
        db.session.add(user)
        db.session.commit()
        flash('Your Account has been created!!!', 'success')
        return redirect(url_for("login"))



    return render_template("login.html", form=form)



  return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)