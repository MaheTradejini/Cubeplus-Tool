from functools import wraps
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
  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost:5432/stocks'
  bcrypt = Bcrypt()

  db.init_app(app)
  bcrypt.init_app(app)

  with app.app_context():
    db.create_all()


  def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

  @app.route("/")
  def home():
    return render_template("home.html")


  @app.route("/login", methods=['GET', 'POST'])
  def login():
    if 'user_id' in session:
        return redirect(url_for("dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('You have been logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    else:
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
    return render_template("login.html", form=form)





  @app.route("/register", methods = ['GET', 'POST'])
  def register():
    if 'user_id' in session:
        return redirect(url_for("dashboard"))
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

    return render_template("register.html", form=form)

  @app.route("/dashboard")
  @login_required
  def dashboard():
    return render_template("dashboard.html")

  @app.route("/logout")
  def logout():
    session.pop('user_id')
    session.pop('username')
    flash('You have been logged out !', 'success')
    return redirect(url_for('home'))



  return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)