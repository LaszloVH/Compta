from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from PyPDF2 import PdfMerger
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
            generate_info_pdf(name, date, amount, reason)

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

        merge_pdfs(folder_name, name)

        return 'Formulaire soumis avec succès!'
    else:
        return 'Format de fichier non pris en charge. Veuillez utiliser un fichier PDF, JPG, JPEG ou PNG.'


def generate_info_pdf(name, date, amount, reason):
    # Créer un fichier PDF avec les informations dans un tableau de 4 colonnes
    pdf = SimpleDocTemplate(f'uploads/{date}-{reason}/info.pdf', pagesize=letter)
    data = [['Blaze :', 'Date :', 'Montant :', 'Raison :'],
            [name, date, amount, reason]]
    table = Table(data)

    # Ajouter un style au tableau pour rendre les bordures apparentes
    style = TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ])
    table.setStyle(style)

    pdf.build([table])


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

def merge_pdfs(folder_name, name):
    # Fusionner les fichiers PDF facture et info
    merger = PdfMerger()
    merger.append(f'{folder_name}/info.pdf')
    merger.append(f'{folder_name}/facture.pdf')
    merger.write(f'{folder_name}/facture-{name}.pdf')
    merger.close()

    #Supprimer les PDF inutiles
    os.remove(f'{folder_name}/facture.pdf')
    os.remove(f'{folder_name}/info.pdf')

@app.route('/download/<filename>')
def download(filename):
    return send_file(f'uploads/{filename}', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)