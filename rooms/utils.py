from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
from django.db.models import Q

def get_available_rooms(room, start_time, end_time):
    """
    Check if a room is available for a specific time period
    """
    from .models import Reservation
    
    # Get all reservations for this room that overlap with the requested time period
    overlapping_reservations = Reservation.objects.filter(
        Q(room=room),
        Q(start_time__lt=end_time) & Q(end_time__gt=start_time),
        ~Q(status='cancelled')
    )
    
    # If there are no overlapping reservations, the room is available
    return not overlapping_reservations.exists()

def get_payment_status(reservation):
    """
    Get the payment status for a reservation
    """
    from .models import Payment
    
    try:
        payment = Payment.objects.get(reservation=reservation)
        return payment.status
    except Payment.DoesNotExist:
        return 'not_initiated'

def get_reservation_status(reservation):
    """
    Get a human-readable status for a reservation
    """
    if reservation.status == 'cancelled':
        return 'Annulée'
    
    if not reservation.is_paid:
        return 'En attente de paiement'
    
    if reservation.status == 'confirmed':
        return 'Confirmée'
    
    return 'En attente'

def generate_reservation_receipt(reservation):
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib.units import cm
    from reportlab.platypus import Image
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import qrcode
    from django.urls import reverse
    from django.conf import settings
    import os
    
    # Register custom fonts
    try:
        pdfmetrics.registerFont(TTFont('Roboto', os.path.join(settings.BASE_DIR, 'static/fonts/Roboto-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('RobotoBold', os.path.join(settings.BASE_DIR, 'static/fonts/Roboto-Bold.ttf')))
        pdfmetrics.registerFont(TTFont('RobotoLight', os.path.join(settings.BASE_DIR, 'static/fonts/Roboto-Light.ttf')))
        font_family = 'Roboto'
        bold_font = 'RobotoBold'
        light_font = 'RobotoLight'
    except:
        # Fallback to standard fonts if custom ones aren't available
        font_family = 'Helvetica'
        bold_font = 'Helvetica-Bold'
        light_font = 'Helvetica'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          leftMargin=0.7*cm, rightMargin=0.7*cm,
                          topMargin=0.7*cm, bottomMargin=0.7*cm)
    styles = getSampleStyleSheet()
    story = []
    
    # Define custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=bold_font,
        fontSize=18,  # Reduced font size
        alignment=TA_CENTER,
        spaceAfter=10,  # Reduced spacing
        textColor=colors.HexColor('#2c3e50')
    )
    
    header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName=bold_font,
        fontSize=12,  # Reduced font size
        textColor=colors.HexColor('#2980b9'),
        spaceAfter=5,  # Reduced spacing
        spaceBefore=5   # Reduced spacing
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_family,
        fontSize=10,
        leading=14
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=normal_style,
        fontName=bold_font,
        textColor=colors.HexColor('#34495e')
    )
    
    value_style = ParagraphStyle(
        'Value',
        parent=normal_style,
        textColor=colors.HexColor('#2c3e50')
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName=light_font,
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_CENTER
    )
    
    # Add company logo if available
    try:
        logo_path = os.path.join(settings.STATIC_ROOT, 'img/logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*cm, height=2*cm)
            story.append(logo)
    except:
        pass  # Skip if logo not available
    
    # Add title
    story.append(Paragraph("Confirmation de Réservation", title_style))
    story.append(Paragraph(f"Réservation #{reservation.id}", header_style))
    story.append(Spacer(1, 5))
    
    # Add reservation details in a nicer table
    # Create a custom styled table for details
    story.append(Paragraph("Détails de la Réservation", header_style))
    
    data = [
        [Paragraph("<b>Salle:</b>", label_style), 
         Paragraph(reservation.room.name, value_style)],
        [Paragraph("<b>Date de début:</b>", label_style), 
         Paragraph(reservation.start_time.strftime('%d/%m/%Y'), value_style)],
        [Paragraph("<b>Heure de début:</b>", label_style), 
         Paragraph(reservation.start_time.strftime('%H:%M'), value_style)],
        [Paragraph("<b>Date de fin:</b>", label_style), 
         Paragraph(reservation.end_time.strftime('%d/%m/%Y'), value_style)],
        [Paragraph("<b>Heure de fin:</b>", label_style), 
         Paragraph(reservation.end_time.strftime('%H:%M'), value_style)],
        [Paragraph("<b>Prix total:</b>", label_style), 
         Paragraph(f"{reservation.total_price:.2f} €", value_style)],
        [Paragraph("<b>Statut:</b>", label_style), 
         Paragraph(get_reservation_status(reservation), value_style)],
    ]
    
    # Calculate duration
    duration = reservation.end_time - reservation.start_time
    hours = duration.total_seconds() / 3600
    data.append([Paragraph("<b>Durée:</b>", label_style), 
                Paragraph(f"{hours:.1f} heures", value_style)])
    
    table = Table(data, colWidths=[3.5*cm, 10.5*cm])  # Adjusted column widths
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Left align labels
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Left align values
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # Reduced padding
        ('TOPPADDING', (0, 0), (-1, -1), 4),     # Reduced padding
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#e9ecef')),
        ('ROUNDEDCORNERS', [3, 3, 3, 3]),        # Smaller corners
    ]))
    
    story.append(table)
    story.append(Spacer(1, 5))
    
    # Add user information
    story.append(Paragraph("Informations de l'utilisateur", header_style))
    
    user_data = [
        [Paragraph("<b>Nom:</b>", label_style), 
         Paragraph(f'{reservation.user.first_name} {reservation.user.last_name}', value_style)],
        [Paragraph("<b>Email:</b>", label_style), 
         Paragraph(reservation.user.email, value_style)],
        [Paragraph("<b>Réservé le:</b>", label_style), 
         Paragraph(reservation.created_at.strftime('%d/%m/%Y %H:%M'), value_style)],
    ]
    
    user_table = Table(user_data, colWidths=[4*cm, 10*cm])
    user_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#e9ecef')),
    ]))
    
    story.append(user_table)
    story.append(Spacer(1, 5))
    
    # Generate QR code
    try:
        # Create the verification URL - adjust based on your URL structure
        verification_url = f"{settings.SITE_URL}{reverse('rooms:download_pdf', args=[reservation.id])}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer)
        qr_buffer.seek(0)
        
        # Create a more compact layout with QR code and text side by side
        story.append(Paragraph("Vérification", header_style))
        
        qr_image = Image(qr_buffer, width=2*cm, height=2*cm)  # Smaller QR code
        qr_table_data = [
            [qr_image, Paragraph("Scannez ce code QR pour vérifier. ID: <b>" + str(reservation.id) + "</b>", normal_style)]
        ]
        
        qr_table = Table(qr_table_data, colWidths=[4*cm, 10*cm])
        qr_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
        ]))
        
        story.append(qr_table)
    except Exception as e:
        # Fallback if QR code generation fails
        story.append(Paragraph(f"ID de vérification: {reservation.id}", normal_style))
    
    story.append(Spacer(1, 5))
    
    # Add terms and conditions
    terms_style = ParagraphStyle(
        'Terms',
        parent=normal_style,
        fontSize=7,  # Smaller font
        leading=8,   # Reduced line spacing
        textColor=colors.gray
    )
    
    terms_text = """<b>Conditions:</b> Annulations moins de 24h à l'avance: frais applicables. Arrivez 15 min avant. Contact: support@example.com"""
    
    story.append(Paragraph(terms_text, terms_style))
    story.append(Spacer(1, 5))
    
    # Add footer with date and page numbers
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    footer_text = f'Document généré le {now} | Système de Réservation | Page 1/1'
    story.append(Paragraph(footer_text, footer_style))
    
    # Build the PDF
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
