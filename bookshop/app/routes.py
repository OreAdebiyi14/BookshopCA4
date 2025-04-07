from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Book
from .forms import RegisterForm, LoginForm, BookForm
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    from .models import Book
    books = Book.query.all()
    return render_template('home.html', books=books)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            password_hash=hashed_password,
            is_admin=form.is_admin.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('main.login'))
    if form.is_admin.data and form.admin_code.data.strip() != "admin123":
        flash("Invalid admin access code", "danger")
        return render_template("register.html", form=form)

    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            if form.is_admin.data and not user.is_admin:
                flash("This account is not an admin!", "danger")
                return redirect(url_for('main.login'))
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@main.route('/admin/books')
@login_required
def admin_books():
    if not current_user.is_admin:
        flash("Access denied", "danger")
        return redirect(url_for('main.home'))
    books = Book.query.all()
    return render_template('admin_books.html', books=books)

@main.route('/admin/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if not current_user.is_admin:
        flash("Access denied", "danger")
        return redirect(url_for('main.home'))
    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            price=form.price.data,
            stock=form.stock.data,
            description=form.description.data
        )
        db.session.add(book)
        db.session.commit()
        flash("Book added successfully", "success")
        return redirect(url_for('main.admin_books'))
    return render_template('book_form.html', form=form)

@main.route('/admin/books/delete/<int:book_id>')
@login_required
def delete_book(book_id):
    if not current_user.is_admin:
        flash("Access denied", "danger")
        return redirect(url_for('main.home'))
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted", "info")
    return redirect(url_for('main.admin_books'))

