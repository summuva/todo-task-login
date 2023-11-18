from flask import Flask, render_template, request, redirect, url_for,flash
from flask_login import LoginManager,login_user, logout_user, login_required, current_user
from database import create_db
from models import Task,User
from forms import LoginForm, RegisterForm, TaskForm


# Configuraciones 
app = Flask(__name__)
app.config.from_object("config.Config")
db = create_db(app)




# Configuracion del login 
login_manager = LoginManager(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    # Esta función carga el usuario a partir de su ID almacenado en la sesión
    return User.query.get(int(user_id))




# Rutas 
@app.route("/", methods=['GET','POST'])
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id)
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data,user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
      
    return render_template("index.html",tasks=tasks,form=form)


@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    task = Task.query.get(id)
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.done = form.done.data
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit.html",form=form,task=task)




@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas. Inténtalo de nuevo.', 'danger')

    return render_template('login.html', form=form)





@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))






@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            return render_template("error.html")
        else:
            newUser = User(username=form.username.data,password=form.password.data)
            db.session.add(newUser)
            db.session.commit()
            return redirect(url_for("login"))
        

    return render_template("register.html",form=form)




if __name__ == "__main__":
    app.run(debug=True)