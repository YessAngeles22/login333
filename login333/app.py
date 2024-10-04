from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from firebase_admin import credentials, firestore
import firebase_admin

app = Flask(__name__)

app.config.from_object('config.Config')

# Initialize Firebase
cred = credentials.Certificate(app.config['FIREBASE_CONFIG'])
firebase_admin.initialize_app(cred)

# Create a reference to the Firestore database
db = firestore.client()

# Create a login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Define a user class
class User(UserMixin):
    def __init__ (self, id, username, email,user_ret):
        self.id = id
        self.username = username
        self.email=email
        self.user_ret = user_ret

        def __repr__(self):
          return f"User('{self.username}', '{self.email}')"

        #Load user from database
        @login_manager.user_loader
        def load_user(user_id):
            user_ref=db.collection('users').document(user_id)
            user_data= user_ret.get().to_dict()
            return User(user_data['id'],user_data['username'],user_data['email'])

        #define routes
        @app.route('/')
        def index():
            return render_template('index.html')

        @app.route('/login',methods=['GET','POST'])
        def login():
            if request.method=='POST':
                username=request.form['username']
                password =request.form['password']
                user_ref =db.collection('users').where('username','==',username).get()
                if user_ref:
                    user_data=user_ref[0].to_dict()
                    if user_data['password']==password:
                        user= User(user_data['id'],user_data['username'],user_data['email'])
                        login_user(user)
                        return redirect(url_for('tasks'))
                    return render_template('login.html')

                @app.route('/logout')
                def logout():
                    logout_user()
                    return redirect(url_for('index'))

                @app.route('/register', methods=['GET','POST'])
                def register():
                    if request.method=='POST':
                        username= request.form['username']
                        email=request.form['email']
                        password=request.form['password']
                        user_ref=db.collection('users').document()
                        user_ref.set({
                            'id':user_ref.id,
                            'username':username,
                            'email':email,
                            'password':password
                            })
                        return redirect(url_for('login'))
                    return render_template('register.html')

                @app.route('/tasks')
                def tasks():

                    tasks_ref = db.collection('tasks').where('user_id', '==', current_user.id).get()

                    tasks = []

                    for task in tasks_ref:

                        task_data = task.to_dict()

                        tasks.append({

                          'id': task.id,

                          'title': task_data['title'],

                          'description': task_data['description'],

                           'due_date': task_data['due_date']
                        })
                        return render_template('tasks.html', tasks=tasks)

                    @app.route('/add_task', methods=['POST'])
                    def add_task():
                        title =request.form['title']
                        description = request.form ['description']
                        due_date = request.form['due_date']
                        task_ref=db.collection('tasks').document()
                        task_ref.set({
                            'id': task_ref.id,
                            'user_id': current_user.id,
                            'title':title,
                            'description': description,
                            'due_date': due_date
                            })
                        return redirect(url_for('tasks'))
                    @app.route('/delete_task/<task_id>')
                    def delete_task(task_id):
                        task_ref=db.collection('tasks').document(task_id)
                        task_ref.delete()
                        return redirect(url_for('tasks'))
                    @app.route('/mark_task_as_completed/<task_id>')
                    def mark_task_as_completed(task_id):
                        task_ref = db.collection('tasks').document(task_id)
                        task_data = task_ref.get().to_dict()
                        task_data['completed'] = True
                        task_ref.set(task_data)
                        return redirect(url_for('tasks'))

                   
                       
                       

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
