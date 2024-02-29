from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont
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
    name = request.form['name']

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

        if rib_file:
            # Gérer le fichier RIB s'il est présent
            rib_filename = f'RIB-{secure_filename(name)}.pdf'  # Renommer le fichier RIB
            rib_path = os.path.join(folder_name, rib_filename)
            rib_file.save(rib_path)

        if file.filename.endswith('.pdf'):
            generate_pdf(amount, date, reason, name, file_path, rib_path if rib_file else None)
        elif file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            generate_image_summary(amount, date, reason, name, file_path, rib_path if rib_file else None)


        return 'Formulaire soumis avec succès!'
    else:
        return 'Format de fichier non pris en charge. Veuillez utiliser un fichier PDF, JPG, JPEG ou PNG.'


def generate_pdf(amount, date, reason, name, file_path, rib_path=None):
    # Modifier le chemin pour enregistrer le fichier dans le dossier approprié
    pdf_output_path = f'{os.path.splitext(file_path)[0]}_récap.pdf'
    c = canvas.Canvas(pdf_output_path)
    c.drawString(100, 750, f'Montant: {amount}')
    c.drawString(100, 730, f'Date: {date}')
    c.drawString(100, 710, f'Motif: {reason}')
    c.save()

def generate_image_summary(amount, date, reason, name, file_path, rib_path=None):
    # Modifier le chemin pour enregistrer le fichier dans le dossier approprié
    img_output_path = f'{os.path.splitext(file_path)[0]}_récap.pdf'
    img = Image.new('RGB', (827 , 1170), color='white')  # Ajustez la taille de l'image selon vos besoins
    d = ImageDraw.Draw(img)

    # Définir la police et la taille du texte
    font = ImageFont.load_default()

    # Ajouter des marges
    margin = 20

    # Ajouter le texte avec des marges
    d.text((margin, margin), f'Montant: {amount}', font=font, fill='black')
    d.text((margin, margin + 20), f'Date: {date}', font=font, fill='black')
    d.text((margin, margin + 40), f'Motif: {reason}', font=font, fill='black')

    # Charger l'image et l'ajouter à l'image créée
    original_image = Image.open(file_path)

    # Redimensionner l'image pour s'adapter à la page
    img_width, img_height = img.size
    original_image.thumbnail((img_width - 2 * margin, img_height - 3 * margin))
    
    # Calculer la position pour centrer l'image
    image_position = ((img_width - original_image.width) // 2, margin + 3 * margin)

    img.paste(original_image, image_position)

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