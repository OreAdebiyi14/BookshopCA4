from os import abort
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import CartItem, Order, Review, User, Book, Item
from .forms import RegisterForm, LoginForm, BookForm, ReviewForm
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    query = request.args.get('q', '')
    sort = request.args.get('sort', '')

    books = Book.query

    if query:
        search = f"%{query}%"
        books = books.filter(
            db.or_(
                Book.title.ilike(search),
                Book.author.ilike(search),
                Book.publisher.ilike(search),
                Book.category.ilike(search)
            )
        )

    # Sorting
    if sort == 'title_asc':
        books = books.order_by(Book.title.asc())
    elif sort == 'title_desc':
        books = books.order_by(Book.title.desc())
    elif sort == 'price_asc':
        books = books.order_by(Book.price.asc())
    elif sort == 'price_desc':
        books = books.order_by(Book.price.desc())

    return render_template('home.html', books=books.all())


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
        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            price=form.price.data,
            stock_quantity=form.stock_quantity.data,
            description=form.description.data
        )
        db.session.add(new_book)
        db.session.commit()
        flash("Book added successfully!", "success")
        return redirect(url_for('main.admin_books'))
    
    return render_template("add_book.html", form=form)

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

@main.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('main.home'))

    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)

    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.price = form.price.data
        book.stock_quantity = form.stock_quantity.data
        book.description = form.description.data
        db.session.commit()
        flash('Book updated successfully.')
        return redirect(url_for('main.admin_books'))

    return render_template('edit_book.html', form=form, book=book)

@main.route('/cart')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.user_id).all()
    return render_template('cart.html', cart_items=cart_items)

@main.route('/cart/add/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    existing = CartItem.query.filter_by(
        user_id=current_user.user_id, 
        book_id=book_id).first()
    if existing:
        existing.quantity += 1
    else:
        new_item = CartItem(
            user_id=current_user.user_id, 
            book_id=book_id, quantity=1)
        db.session.add(new_item)
    db.session.commit()
    flash('Book added to cart!')
    return redirect(url_for('main.home'))

@main.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.user_id:
        flash("Unauthorized access.")
        return redirect(url_for('main.view_cart'))
    db.session.delete(item)
    db.session.commit()
    flash('Item removed.')
    return redirect(url_for('main.view_cart'))

@main.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_quantity(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.user_id:
        flash("Unauthorized", "danger")
        return redirect(url_for('main.view_cart'))

    try:
        new_quantity = int(request.form.get('quantity'))
        print(f"Received quantity: {new_quantity}")
        if new_quantity < 1:
            db.session.delete(item)
        else:
            item.quantity = new_quantity
        db.session.commit()
        flash('Cart updated.', 'success')
    except Exception as e:
        flash('Invalid quantity.', 'danger')
        print(f"Error: {e}")
    return redirect(url_for('main.view_cart'))

@main.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.user_id).all()

    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('main.view_cart'))

    total = sum(item.book.price * item.quantity for item in cart_items)

    # Create a new order
    new_order = Order(
        user_id=current_user.user_id,
        total_price=total,
        status='Pending'  # You can update this later to 'Paid' or 'Shipped'
    )
    db.session.add(new_order)
    db.session.flush()  # Gets new_order.order_id before committing

    # Create each item for this order
    for item in cart_items:
        order_item = Item(
            order_id=new_order.order_id,
            book_id=item.book_id,
            quantity=item.quantity,
            price_at_purchase=item.book.price
        )
        db.session.add(order_item)

    # Clear the user's cart
    for item in cart_items:
        db.session.delete(item)

    db.session.commit()
    flash('Your order has been placed successfully!', 'success')
    return redirect(url_for('main.order_confirmation', order_id=new_order.order_id))

@main.route("/orders")
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.user_id).order_by(Order.order_id.desc()).all()
    return render_template("order_history.html", orders=orders)

@main.route('/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.user_id and not current_user.is_admin:
        abort(403)
    items = Item.query.filter_by(order_id=order_id).all()
    return render_template('order_confirmation.html', order=order, items=items)

@main.context_processor
def inject_cart_count():
    if current_user.is_authenticated:
        count = CartItem.query.filter_by(user_id=current_user.user_id).count()
        return {'cart_count': count}
    return {'cart_count': 0}

@main.route('/admin/books/<int:book_id>/stock', methods=['POST'])
@login_required
def update_stock(book_id):
    if not current_user.is_admin:
        abort(403)

    book = Book.query.get_or_404(book_id)
    try:
        new_stock = int(request.form.get('stock'))
        book.stock_quantity = max(new_stock, 0)
        db.session.commit()
        flash(f"Stock updated for {book.title}.", "success")
    except ValueError:
        flash("Invalid stock number.", "danger")

    return redirect(url_for('main.admin_books'))

@main.route("/books/<int:book_id>/review", methods=["GET", "POST"])
@login_required
def review_book(book_id):
    book = Book.query.get_or_404(book_id)
    review = Review.query.filter_by(user_id=current_user.user_id, book_id=book_id).first()
    form = ReviewForm(obj=review)

    if form.validate_on_submit():
        if review:
            review.rating = form.rating.data
            review.comment = form.comment.data
        else:
            review = Review(
                user_id=current_user.user_id,
                book_id=book_id,
                rating=form.rating.data,
                comment=form.comment.data
            )
            db.session.add(review)

        db.session.commit()
        flash("Your review has been submitted!", "success")
        return redirect(url_for("main.book_details", book_id=book_id))

    return render_template("review_book.html", form=form, book=book, is_edit=bool(review))

@main.route('/books/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_details.html', book=book)
