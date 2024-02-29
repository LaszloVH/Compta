from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw
from io import BytesIO
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    amount = request.form['amount']
    date = request.form['date']
    reason = request.form['reason']

    file = request.files['file']

    if file.filename.endswith(('.pdf', '.jpg', '.jpeg', '.png')):
        # Utilisez secure_filename pour obtenir un nom de fichier sûr
        filename = secure_filename(file.filename)
        
        # Créer un dossier avec le nom approprié s'il n'existe pas
        folder_name = f'uploads/{date}-{reason}'
        os.makedirs(folder_name, exist_ok=True)
        
        # Sauvegarder le fichier dans le dossier créé
        file_path = os.path.join(folder_name, filename)
        file.save(file_path)

        if file.filename.endswith('.pdf'):
            generate_pdf(amount, date, reason, file_path)
        elif file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            generate_image_summary(amount, date, reason, file_path)

        return 'Formulaire soumis avec succès!'
    else:
        return 'Format de fichier non pris en charge. Veuillez utiliser un fichier PDF, JPG, JPEG ou PNG.'

def generate_pdf(amount, date, reason, file_path):
    # Modifier le chemin pour enregistrer le fichier dans le dossier approprié
    pdf_output_path = f'{os.path.splitext(file_path)[0]}_récap.pdf'
    c = canvas.Canvas(pdf_output_path)
    c.drawString(100, 750, f'Montant: {amount}')
    c.drawString(100, 730, f'Date: {date}')
    c.drawString(100, 710, f'Motif: {reason}')
    c.save()

def generate_image_summary(amount, date, reason, file_path):
    # Modifier le chemin pour enregistrer le fichier dans le dossier approprié
    img_output_path = f'{os.path.splitext(file_path)[0]}_récap.pdf'
    img = Image.new('RGB', (400, 200), color='white')
    d = ImageDraw.Draw(img)
    d.text((10, 10), f'Montant: {amount}', fill='black')
    d.text((10, 30), f'Date: {date}', fill='black')
    d.text((10, 50), f'Motif: {reason}', fill='black')

    # Charger l'image et l'ajouter à l'image créée
    original_image = Image.open(file_path)
    img.paste(original_image, (150, 70))

    # Enregistrer l'image composée au format PDF
    img.save(img_output_path, format='PDF')

    # Vous pouvez supprimer le fichier image temporaire si vous le souhaitez
    os.remove(file_path)

    # Envoyer le fichier PDF en réponse
    return send_file(img_output_path, as_attachment=True)

@app.route('/download/<filename>')
def download(filename):
    return send_file(f'uploads/{filename}', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
