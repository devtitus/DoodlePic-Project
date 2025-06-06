from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import cv2
import numpy as np
import threading
import time
import glob
import uuid

# Disable pygame audio to prevent ALSA errors on headless/mobile environments
os.environ['SDL_AUDIODRIVER'] = 'dummy'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'

def cleanup_old_files():
    """Remove all files from upload and output directories"""
    try:
        # Clean upload folder
        upload_files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*'))
        for file_path in upload_files:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Removed upload file: {file_path}")
        
        # Clean output folder
        output_files = glob.glob(os.path.join(app.config['OUTPUT_FOLDER'], '*'))
        for file_path in output_files:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Removed output file: {file_path}")
                
    except Exception as e:
        print(f"Error cleaning up files: {e}")

def periodic_cleanup():
    """Run cleanup every 30 minutes"""
    while True:
        time.sleep(1800)  # 30 minutes
        cleanup_old_files()
        print("Periodic cleanup completed")

# Start cleanup thread
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()

def sketch_image(image_path):
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Unable to load the image at path: {image_path}")

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Invert the grayscale image
    inverted_gray_image = 255 - gray_image

    # Apply GaussianBlur to the inverted image
    blurred_image = cv2.GaussianBlur(inverted_gray_image, (21, 21), 0)

    # Invert the blurred image
    inverted_blurred_image = 255 - blurred_image

    # Create the sketch image by combining the inverted blurred image with the original grayscale image
    sketch_image = cv2.divide(gray_image, inverted_blurred_image, scale=256.0)

    return sketch_image

def save_sketch_image(sketch_image, output_path):
    """Save sketch image using OpenCV - more reliable and no audio dependencies"""
    try:
        # OpenCV handles image saving efficiently without requiring audio libraries
        cv2.imwrite(output_path, sketch_image)
        print(f"Sketch saved successfully: {output_path}")
    except Exception as e:
        print(f"Error saving sketch: {e}")
        raise e

@app.route('/')
def upload_form():
    # Clean up old files when user visits homepage
    cleanup_old_files()
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    # Clean up old files before processing new upload
    cleanup_old_files()
    
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '' or file.filename is None:
        return redirect(request.url)
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return redirect(url_for('upload_form', error='invalid_type'))
    
    # Check file size (5MB limit)
    file_content = file.read()
    if len(file_content) > 5 * 1024 * 1024:  # 5MB in bytes
        return redirect(url_for('upload_form', error='file_too_large'))
    
    file.seek(0)  # Reset file pointer after validation
    
    # Create directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    if file:
        try:
            # Generate unique filename to avoid conflicts
            unique_id = str(uuid.uuid4())[:8]
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            upload_filename = f"upload_{unique_id}.{file_extension}"
            
            # Save uploaded file
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)
            file.save(upload_path)            # Process the image and save the output
            sketch = sketch_image(upload_path)
            output_filename = f'sketch_{unique_id}.png'
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            save_sketch_image(sketch, output_path)
            
            # Clean up the uploaded file after processing
            if os.path.exists(upload_path):
                os.remove(upload_path)
                print(f"Cleaned up upload file: {upload_path}")

            return redirect(url_for('display_output', filename=output_filename))
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return redirect(url_for('upload_form', error='processing_error'))
    
    return redirect(request.url)

@app.route('/output/<filename>')
def display_output(filename):
    # Check if file exists
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if not os.path.exists(file_path):
        return redirect(url_for('upload_form', error='file_not_found'))
    return render_template('output.html', filename=filename)

@app.route('/cleanup', methods=['POST'])
def manual_cleanup():
    """Manual cleanup endpoint for frontend"""
    cleanup_old_files()
    return {'status': 'success', 'message': 'Cleanup completed'}

@app.route('/static/output/<filename>')
def send_output(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    else:
        return redirect(url_for('upload_form', error='file_not_found'))

@app.route('/robots.txt')
def robots_txt():
    """Serve robots.txt file for search engine crawlers"""
    return send_from_directory('static', 'robots.txt', mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap_xml():
    """Serve sitemap.xml file for search engines"""
    return send_from_directory('static', 'sitemap.xml', mimetype='application/xml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
