from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import cv2
import pygame
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'

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

def draw_sketch_pygame(sketch_image, output_path):
    pygame.init()
    width = len(sketch_image[0])
    height = len(sketch_image)
    screen = pygame.Surface((width, height))

    for y in range(height):
        for x in range(width):
            color = sketch_image[y][x]
            screen.set_at((x, y), (color, color, color))

    pygame.image.save(screen, output_path)
    pygame.quit()

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the image and save the output
        sketch = sketch_image(filepath)
        output_filename = 'sketch.png'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        draw_sketch_pygame(sketch, output_path)

        return redirect(url_for('display_output', filename=output_filename))
    return redirect(request.url)

@app.route('/output/<filename>')
def display_output(filename):
    return render_template('output.html', filename=filename)

@app.route('/static/output/<filename>')
def send_output(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
