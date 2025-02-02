
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from markupsafe import Markup
from app import app, db, login_manager, cache
from models import *
from sqlalchemy.exc import SQLAlchemyError  # Import SQLAlchemyError

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

# Route for the facilities page
@app.route('/facilities')
def facilities():
    return render_template('facilities.html')

# Route for the contact form, handles both GET and POST methods
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        contact_number = request.form.get('contact_number')
        city = request.form.get('city', '')

        # Simple form validation
        if not first_name or not last_name or not email or not subject:
            flash('All fields are required!', 'danger')
            return redirect(url_for('contact'))

        if not (contact_number.isdigit() and len(contact_number) == 10):
            flash('Contact number must be exactly 10 digits!', 'danger')
            return redirect(url_for('contact'))

        # Create a new contact entry
        try:
            contact = Contact(
                first_name=first_name,
                last_name=last_name,
                email=email,
                subject=subject,
                contact_number=contact_number,
                city=city
            )
            db.session.add(contact)
            db.session.commit()
            flash('Form submitted successfully!', 'success')
            return redirect(url_for('contact'))
        except SQLAlchemyError as e:
            print(f"Error saving contact: {e}")
            db.session.rollback()
            flash('An error occurred while processing your request. Please try again later.', 'danger')

    return render_template('contact.html')

# Route to view contact information, requires user to be logged in
@app.route('/contact_info', methods=['POST'])
@login_required
def contacts():
    users = Contact.query.all()
    return render_template('contact_info.html', users=users)

# Route for the events page
@app.route('/event')
def event():
    cache_key = 'event_data'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    events = Event.query.all()

    # Render the template and cache the result
    rendered_template = render_template('event.html', events=events)
    cache.set(cache_key, rendered_template, timeout=app.config['CACHE_TIMEOUT'])

    return rendered_template


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

@app.route('/delete_event_image/<int:id>', methods=['POST'])
@login_required
def delete_event_image(id):
    print(f"Delete request received for id: {id}")
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    # flash('Event deleted successfully.', 'success')
    return redirect(url_for('event'))


@app.route('/delete_gallery_image/<int:id>', methods=['POST'])
@login_required
def delete_gallery_image(id):
    print(f"Delete request received for id: {id}")
    event = Image.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    # flash('Event deleted successfully.', 'success')
    return redirect(url_for('gallery'))



@app.route('/delete_faculty_image/<int:id>', methods=['POST'])
@login_required
def delete_faculty_image(id):
    print(f"Delete request received for id: {id}")
    event = Faculty.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    # flash('Event deleted successfully.', 'success')
    return redirect(url_for('faculty'))

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

# Route for event image and description upload, requires user to be logged in
@app.route('/event-upload', methods=['GET', 'POST'])
@login_required
def event_upload():
    if request.method == 'POST':
        image_file = request.files.get('image')
        description = request.form.get('description')

        if image_file and description:
            image_name = image_file.filename
            image_data = image_file.read()

            new_event = Event(image_name=image_name, image_data=image_data, description=description)
            try:
                db.session.add(new_event)
                db.session.commit()
                flash('Image and text uploaded successfully!', 'success')
                return redirect(url_for('event_upload'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {e}', 'danger')
        else:
            flash('Please provide both image and description.', 'danger')
    return render_template('upload.html')

# Route for the faculty page with Redis caching
@app.route('/faculty')
def faculty():
    cache_key = 'faculty_data'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    all_members = Faculty.query.all()

    # Convert image data to base64 strings
    for member in all_members:
        if member.image_data:
            member.base64_data = base64.b64encode(member.image_data).decode('utf-8')
        else:
            member.base64_data = None

    # Separate members by designation
    principals = [member for member in all_members if member.designation == 'Principal']
    vp_and_adm = [member for member in all_members if member.designation in ['Administrator', 'Vice Principal']]
    others = [member for member in all_members if member.designation not in ['Principal', 'Vice Principal', 'Administrator']]

    # Render the template and cache the result
    rendered_template = render_template('faculty.html', principals=principals, vp_and_adm=vp_and_adm, others=others)
    cache.set(cache_key, rendered_template, timeout=app.config['CACHE_TIMEOUT'])

    return rendered_template

# Route for the alumni page
@app.route('/alumni')
def alumni():
    events = Event.query.all()
    return render_template('alumni.html')

# Route for faculty information upload, requires user to be logged in
@app.route('/faculty-upload', methods=['GET', 'POST'])
@login_required
def faculty_upload():
    if request.method == 'POST':
        faculty_image = request.files.get('faculty_image')
        faculty_name = request.form.get('faculty_name')
        faculty_designation = request.form.get('faculty_designation')
        faculty_qualification = request.form.get('faculty_qualification')
        faculty_age = request.form.get('faculty_age')
        faculty_experience = request.form.get('faculty_experience')

        # Basic validation
        if not faculty_image or not faculty_name or not faculty_age or not faculty_experience or not faculty_qualification:
            flash('All fields are required!', 'danger')
            return redirect(url_for('faculty_upload'))

        # Read the image data
        image_name = faculty_image.filename
        image_data = faculty_image.read()

        # Create a new faculty entry
        new_faculty = Faculty(
            image_name=image_name,
            image_data=image_data,
            name=faculty_name,
            designation=faculty_designation,
            qualification=faculty_qualification,
            age=faculty_age,
            experience=faculty_experience
        )

        try:
            db.session.add(new_faculty)
            db.session.commit()
            flash('Faculty information uploaded successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')

        return redirect(url_for('faculty_upload'))

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
