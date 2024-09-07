from django.shortcuts import redirect, render
import io
import google.generativeai as genai
from django.http import HttpResponse, HttpResponseRedirect
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

from crop_app.models import ImageModel


# Configure Gemini API
genai.configure(api_key="AIzaSyALLmlsEYf8GlssEM9YuR0KfWs5V5nre5M")

def generate_report(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')

        # Step 1: Fetch content from Gemini API based on user input
        try:
            response_text = fetch_from_gemini(user_input)
        except Exception as e:
            return HttpResponse(f'Error: {e}', status=500)

        # Step 2: Generate PDF with fetched content
        try:
            pdf_buffer = generate_pdf(response_text)
            return HttpResponse(pdf_buffer, content_type='application/pdf')
        except Exception as e:
            return HttpResponse(f'Error: {e}', status=500)
    else:
        return render(request, 'generate_report.html')

def fetch_from_gemini(user_input):
    # Create a chat session with Gemini API
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 150,
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(history=[{"role": "user", "parts": [user_input]}])
    response = chat_session.send_message(user_input)
    
    return response.text

def generate_pdf(text_content):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica", 12)

    width, height = A4
    margin = 50  # Set margins for all four sides
    line_height = 20  # Adjust line height

    # Start writing from the top, considering the margin
    y_position = height - margin

    # Split the text into lines, breaking long lines if necessary
    lines = text_content.split('\n')

    for line in lines:
        # Remove markdown symbols (#, *) from the line
        clean_line = line.replace('#', '').replace('*', '').strip()

        # Check if the line is a heading (e.g., starting with "##" for markdown-like headings)
        if line.startswith("##"):
            # Center-align the heading
            wrapped_lines = simpleSplit(clean_line, "Helvetica", 12, width - 2 * margin)
            for wrapped_line in wrapped_lines:
                text_width = pdf.stringWidth(wrapped_line, "Helvetica", 12)
                x_position = (width - text_width) / 2  # Calculate the center
                pdf.drawString(x_position, y_position, wrapped_line)
                y_position -= line_height  # Move down for the next line
        else:
            # Left-align the rest of the content
            wrapped_lines = simpleSplit(clean_line, "Helvetica", 12, width - 2 * margin)
            for wrapped_line in wrapped_lines:
                pdf.drawString(margin, y_position, wrapped_line)
                y_position -= line_height  # Move down for the next line

        # Check if we need to create a new page
        if y_position < margin:
            pdf.showPage()  # Create a new page
            y_position = height - margin  # Reset y_position for new page
            pdf.setFont("Helvetica", 12)  # Reset font for the new page

    pdf.showPage()  # Ensure the last page is committed
    pdf.save()
    buffer.seek(0)

    return buffer


import requests
from django.shortcuts import render

def get_wordpress_posts(request):
    url = "https://sushmitha.socialmm.in/wp-json/wp/v2/posts"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        if response.headers.get('content-type') == 'application/json; charset=UTF-8':
            posts = response.json()  # Parse JSON if the content is valid
            return render(request, 'posts.html', {'posts': posts})
        else:
            return HttpResponse(f"Invalid content type: {response.headers.get('content-type')}", status=500)

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Request failed: {str(e)}", status=500)
    except ValueError as e:
        return HttpResponse(f"Invalid JSON response: {str(e)}", status=500)

def capture_image(request):
    if request.method == 'POST' and 'image' in request.FILES:
        image_file = request.FILES['image']
        image_instance = ImageModel(image=image_file)
        image_instance.save()
        return redirect('admin:index')
    return render(request, 'capture_image.html')

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')
