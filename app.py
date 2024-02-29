from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from pdf2image import convert_from_path
from PyPDF2 import PdfFileMerger
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from werkzeug.utils import secure_filename
import os
import img2pdf

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    date = request.form['date']
    amount = request.form['amount']
    reason = request.form['reason']
    
    file = request.files['file']
    rib_file = request.files.get('rib')  # Utilisez get pour éviter une KeyError si le champ n'est pas présent

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
            generate_info_pdf(name, date, amount, reason)
        elif file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            generate_facture_pdf(file_path, folder_name)

        if rib_file:
            # Sauvegarder le fichier dans le dossier créé
            rib_filename = secure_filename(rib_file.filename)
            rib_file_path = os.path.join(folder_name, rib_filename)
            rib_file.save(rib_file_path)

        # Si le fichier RIB est déjà un PDF, le renommer en RIB-{Nom}.pdf
        if rib_filename.lower().endswith('.pdf'):
            os.rename(rib_file_path, os.path.join(folder_name, f"RIB-{name}.pdf"))
        else:
            # Sinon, convertir l'image en PDF
            generate_rib_pdf(rib_file_path, folder_name, name)


        return 'Formulaire soumis avec succès!'
    else:
        return 'Format de fichier non pris en charge. Veuillez utiliser un fichier PDF, JPG, JPEG ou PNG.'


def generate_info_pdf(name, date, amount, reason):
    # Modifier le chemin pour enregistrer le fichier dans le dossier approprié
    pdf_output_path = f'{os.path.splitext(file_path)[0]}_info.pdf'
    c = canvas.Canvas(pdf_output_path)
    c.drawString(100, 710, f'Blaze: {name}')
    c.drawString(100, 730, f'Date: {date}')
    c.drawString(100, 750, f'Montant: {amount}')
    c.drawString(100, 770, f'Motif: {reason}')
    c.save()

def generate_facture_pdf(file_path, folder_name):

    # Ouvrir l'image et la convertir en PDF
    with open(file_path, "rb") as img_file, open(os.path.join(folder_name, "facture.pdf"), "wb") as pdf_file:
        pdf_bytes = img2pdf.convert(img_file.read())
        pdf_file.write(pdf_bytes)

    # Supprimer l'image
    os.remove(file_path)

def generate_rib_pdf(rib_file_path, folder_name, name):
    
    # Ouvrir l'image et la convertir en PDF
    with open(rib_file_path, "rb") as img_file, open(os.path.join(folder_name, f"RIB-{name}.pdf"), "wb") as pdf_file:
        pdf_bytes = img2pdf.convert(img_file.read())
        pdf_file.write(pdf_bytes)

    # Supprimer l'image
    os.remove(rib_file_path)
    

@app.route('/download/<filename>')
def download(filename):
    return send_file(f'uploads/{filename}', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)