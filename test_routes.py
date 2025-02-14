
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
# @app.route('/facilities')
# def facilities():
#     return render_template('services.html')





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



# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
#     # Retrieve service name from query parameters
#     name = request.args.get('service_name', '')
#     # Fetch service from the database based on the service_name
#     service = Service.query.filter_by(title=name).first()
#     # Check if the service exists, and if so, fetch the amount and title
#     service_name = service.title if service else "not found"
#     service_amount = service.amount if service else "not found"
#     if request.method == 'POST':
#         # Retrieve form data
#         first_name = request.form.get('first_name')
#         last_name = request.form.get('last_name')
#         email = request.form.get('email')
#         subject = request.form.get('subject')  # This is the service name passed from the URL
#         contact_number = request.form.get('contact_number')
#         city = request.form.get('city', '')
#         # Simple form validation
#         if not first_name or not last_name or not email or not subject:
#             flash('All fields are required!', 'danger')
#             return redirect(url_for('contact', service_name=service_name))
#         if not (contact_number.isdigit() and len(contact_number) == 10):
#             flash('Contact number must be exactly 10 digits!', 'danger')
#             return redirect(url_for('contact', service_name=service_name))
#         # Create a new contact entry
#         try:
#             contact = Contact(
#                 first_name=first_name,
#                 last_name=last_name,
#                 email=email,
#                 subject=subject,
#                 contact_number=contact_number,
#                 city=city
#             )
#             db.session.add(contact)
#             db.session.commit()
#             flash('Form submitted successfully!', 'success')
#             # Redirect to the appointments page
#             return redirect(url_for('home'))
#         except SQLAlchemyError as e:
#             print(f"Error saving contact: {e}")
#             db.session.rollback()
#             flash('An error occurred while processing your request. Please try again later.', 'danger')
#     return render_template('contact.html', service_name=service_name, service_amount=service_amount)


# Route to view contact information, requires user to be logged in
@app.route('/contact_info', methods=['POST'])
@login_required
def contacts():
    users = Contact.query.all()
    return render_template('contact_info.html', users=users)


@app.route('/services')
def services():
    all_services = Service.query.all()
    return render_template('services.html', services=all_services)

from flask import jsonify

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    subject = request.form.get('subject')  # This is the service name
    email = request.form.get('email')
    city = request.form.get('city')
    contact_number = request.form.get('contact_number')

    # Validate input
    if not first_name or not last_name or not subject or not email or not contact_number:
        return jsonify({'status': 'error', 'message': 'All fields are required!'})

    if not (contact_number.isdigit() and len(contact_number) == 10):
        return jsonify({'status': 'error', 'message': 'Contact number must be exactly 10 digits!'})

    # Save appointment
    try:
        new_appointment = Appointment(
            first_name=first_name,
            last_name=last_name,
            service_name=subject,
            email=email,
            city=city,
            contact_number=contact_number
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
                'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for a in appointments
        ]

        return jsonify({'status': 'success', 'message': 'Appointment booked successfully!', 'appointments': appointments_data})

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



# @app.route('/services',methods=['GET', 'POST'])
# def services():
#     return render_template('facilities.html')


# Define your services
# services_list = [
#     {"service_name":"Stress_Management","title": "Stress Management", "image": "images/services/STRESS_MANAGEMENT.png"},
#     {"service_name":"Diabetes_Mellitus","title": "Diabetes Mellitus", "image": "images/services/DIABETES_MELLITUS.png"},
#     {"service_name":"Digestive_Disorder","title": "Digestive Disorder", "image": "images/services/DIGESTIVE_DISORDER.png"},
#     {"service_name":"Hyperthyroidism","title": "Hyperthyroidism", "image": "images/services/HYPER_THYROIDISM.png"},
#     {"service_name":"Hypertension","title": "Hypertension", "image": "images/services/hypertension.png"},
#     {"service_name":"Osteoarthritis","title": "Osteoarthritis", "image": "images/services/OSTEOARTHRITIS.png"},
#     {"service_name":"Rheumatoid_Arthritis","title": "Rheumatoid Arthritis", "image": "images/services/RHEUMATOID_ARTHRITIS.png"},
#     {"service_name":"PCOD","title": "PCOD", "image": "images/services/pcod.png"},
#     {"service_name":"Psoriasis","title": "Psoriasis", "image": "images/services/psoriasis.png"},
# ]
# @app.route('/services',methods=['GET', 'POST'])
# def services():
#     # per_page = 3  # Number of services per page
#     # page = request.args.get('page', 1, type=int)
    
#     # # Calculate start and end indices
#     # start = (page - 1) * per_page
#     # end = start + per_page
#     # paginated_services = services[start:end]
    
#     # total_pages = -(-len(services) // per_page)  # Ceiling division
    
#     return render_template("services.html",services=services_list)





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












