from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

# create and configure a Flask application (M)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:uDacity$@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create a SQLAlchemy object to interact with the Flask application (M)
db = SQLAlchemy(app)

# create a Migrate object to handle db migration files
migrate = Migrate(app, db)

# create a specified Model class that mirrors the table in database (M)
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False, default=1)

    # this method is useful for debugging
    def __repr__(self):
        return f'<Todo {self.id}, {self.description}>'

class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

# OLD -- implement the changes in the database (through SQLAlchemy(Flask))  (M)
# db.create_all()
# NEW -- changes implement through Migrate(Flask, SQLAlchemy(Flask))
# using bash $ flask db migrate


# handle routes (C)
@app.route('/')
def index():
    return redirect(url_for('get_todos_by_list', list_id=1))

@app.route('/lists/<list_id>')
def get_todos_by_list(list_id):
    return render_template('index.html',
                           active_list=TodoList.query.get(list_id),
                           todolists=TodoList.query.order_by('id').all(),
                           todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())  # data is dynamically retrieved from db

@app.route('/lists/create', methods=['POST'])
def create_todolist():
    error = False
    body = {}
    try:
        # ASYNCHRONOUS
        name = request.get_json()['name']

        new_todo_list = TodoList(name=name)

        # persist in db
        db.session.add(new_todo_list)
        db.session.commit()
        body['name'] = new_todo_list.name

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        abort(400)

    else:
        # ASYNCHRONOUS
        return jsonify(body)


@app.route('/todos/create/<list_id>', methods=['POST'])
def create_todo(list_id):
    error = False
    body = {}
    try:
        # SYNCHRONOUS: parse_data, create new todo_item
        # description = request.form.get('description', '')

        # ASYNCHRONOUS
        description = request.get_json()['description']

        new_todo_item = Todo(description=description, list_id=list_id)

        # persist in db
        db.session.add(new_todo_item)
        db.session.commit()
        body['description'] = new_todo_item.description

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        abort(400)

    else:
        # SYNCHRONOUS: return a view
        # return redirect(url_for('index'))

        # ASYNCHRONOUS
        return jsonify(body)

@app.route('/todos/<todo_id>/update', methods=['POST'])
def update_todo(todo_id):
    error = False
    try:
        newCompleted = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = newCompleted
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        abort(400)

    else:
        return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    error = False
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        abort(400)

    else:
        return jsonify()  # redirect(url_for('index'))

