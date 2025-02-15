
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from markupsafe import Markup
from app import app, db, login_manager, cache
from models import *
from sqlalchemy.exc import SQLAlchemyError  # Import SQLAlchemyError
from werkzeug.utils import secure_filename
import os
from flask import jsonify
import base64
import json

# Define a custom Jinja filter for base64 encoding
@app.template_filter('b64encode')
def b64encode_filter(data):
    return Markup(base64.b64encode(data).decode('utf-8'))

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        contact = Contact(
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            subject=request.form.get('subject'),
            message=request.form.get('message')
        )
        db.session.add(contact)
        db.session.commit()
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')



# Route to view contact information, requires user to be logged in
@app.route('/contact_info', methods=['POST'])
@login_required
def contacts():
    users = Contact.query.all()
    return render_template('contact_info.html', users=users)


@app.route('/services')
def services():
    all_services = Service.query.all()

    # Convert image binary data to Base64
    for service in all_services:
        if service.image_data:
            service.image_base64 = base64.b64encode(service.image_data).decode('utf-8')

    return render_template('services.html', services=all_services)


@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    service_name = request.form.get('service_name')  # This is the service name
    email = request.form.get('email')
    city = request.form.get('city')
    contact_number = request.form.get('contact_number')
    amount = request.form.get('amount')  # Get the amount

    # Validate input
    if not first_name or not last_name or not service_name  or not email or not contact_number or not amount:
        return jsonify({'status': 'error', 'message': 'All fields are required!'})

    if not (contact_number.isdigit() and len(contact_number) == 10):
        return jsonify({'status': 'error', 'message': 'Contact number must be exactly 10 digits!'})

   
    # Save appointment
    try:
        new_appointment = Appointment(
            first_name=first_name,
            last_name=last_name,
            service_name=service_name,
            email=email,
            city=city,
            contact_number=contact_number,
            amount=float(amount)  # Store amount as a float
        )
        db.session.add(new_appointment)
        db.session.commit()

        # Fetch all appointments to return
        appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
        appointments_data = [
            {
                'id': a.id,
                'first_name': a.first_name,
                'last_name': a.last_name,
                'service_name': a.service_name,
                'email': a.email,
                'city': a.city,
                'contact_number': a.contact_number,
                'amount': a.amount,  # Include amount in the response
                'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for a in appointments
        ]

        return jsonify({'status': 'success', 'message': 'Appointment booked successfully!', 'appointments': appointments_data})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error booking appointment: {e}'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error booking appointment: {e}'})



@app.route('/appointments')
def view_appointments():
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    return render_template('appointments.html', appointments=appointments)



# Route for image uploads, requires user to be logged in
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        image_files = request.files.getlist('images')
        if not image_files:
            flash('No images selected for upload.', 'danger')
            return redirect(url_for('upload'))

        try:
            for image_file in image_files:
                if image_file:
                    image_name = image_file.filename
                    image_data = image_file.read()
                    new_image = Image(image_name=image_name, image_data=image_data)
                    db.session.add(new_image)
            db.session.commit()
            flash('Images uploaded successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
        
        return redirect(url_for('upload'))

    return render_template('upload.html')




@app.route('/delete_gallery_image/<int:id>', methods=['POST'])
@login_required
def delete_gallery_image(id):
    print(f"Delete request received for id: {id}")
    event = Image.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    # flash('Event deleted successfully.', 'success')
    return redirect(url_for('gallery'))





# Route for the gallery page with pagination and image base64 encoding
@app.route('/gallery')
def gallery():
    page = request.args.get('page', 1, type=int)
    cache_key = f'gallery_data_page_{page}'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    per_page = 6
    pagination = Image.query.paginate(page=page, per_page=per_page, error_out=False)
    images = pagination.items

    # Convert image data to base64 for display
    for image in images:
        image.base64_data = base64.b64encode(image.image_data).decode('utf-8')

    # Render the template and cache the result
    rendered_template = render_template('gallery.html', images=images, pagination=pagination)
    cache.set(cache_key, rendered_template, timeout=app.config['CACHE_TIMEOUT'])

    return rendered_template



# Route to delete an image
@app.route('/delete_image', methods=['POST'])
def delete_image():
    image_id = request.form.get('id')
    image = Image.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully.', 'success')
    return redirect(url_for('upload'))

# Route for service image and description upload, requires user to be logged in


@app.route('/service-upload', methods=['GET', 'POST'])
@login_required
def service_upload():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        amount = request.form.get('amount')
        image_file = request.files.get('image')

        if not title or not description or not amount or not image_file:
            flash('All fields are required!', 'danger')
            return redirect(url_for('service_upload'))

        if not amount.isdigit():
            flash('Amount must be a number!', 'danger')
            return redirect(url_for('service_upload'))

        # Read image data
        image_filename = secure_filename(image_file.filename)  # Secure filename
        image_data = image_file.read()  # Read binary data

        # Save service details in the database
        new_service = Service(
            title=title,
            description=description,
            amount=float(amount),
            image_name=image_filename,  # Save filename
            image_data=image_data  # Save binary data
        )

        try:
            db.session.add(new_service)
            db.session.commit()
            flash('Service uploaded successfully!', 'success')
            return redirect(url_for('service_upload'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')

    return render_template('upload.html')




# Function to load a user by their ID for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user and user.password == password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('upload'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

# Route for user logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))












