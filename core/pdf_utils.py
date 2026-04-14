"""
PDF generation utilities for PanchkarmaSetu.
Exactly matches the user-provided design specifications.
"""
from io import BytesIO
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)

# ── Colors from Screenshot ──────────────────────────────────
# Brand Colors
COLOR_BRAND_GREEN = colors.HexColor('#10B981')
COLOR_BRAND_TEXT  = colors.HexColor('#1F2937')
# Status Colors
COLOR_SUCCESS_BG   = colors.HexColor('#F0FDF4')
COLOR_SUCCESS_TEXT = colors.HexColor('#059669')
COLOR_SUCCESS_BRD  = colors.HexColor('#10B981')
# Main Palette
COLOR_PRIMARY   = colors.HexColor('#374151') # Primary text
COLOR_SECONDARY = colors.HexColor('#6B7280') # Headers / Labels
COLOR_MUTED     = colors.HexColor('#9CA3AF') # Interpretations / Small text
COLOR_BORDER    = colors.HexColor('#E5E7EB')
COLOR_TABLE_BG  = colors.HexColor('#F9FAFB')
COLOR_ORANGE    = colors.HexColor('#F59E0B')
COLOR_ORANGE_BG = colors.HexColor('#FFFBEB')

WHITE = colors.white
W, H = A4

# ── Styles ──────────────────────────────────────────────────

def _get_styles():
    return {
        'brand': ParagraphStyle('brand', fontSize=18, fontName='Helvetica-Bold',
                                textColor=COLOR_BRAND_GREEN),
        # Helper for the "Setu" part which is black
        'brand_dark': ParagraphStyle('brand_dark', fontSize=18, fontName='Helvetica-Bold',
                                     textColor=COLOR_BRAND_TEXT),
        
        'header_right': ParagraphStyle('hr', fontSize=10, fontName='Helvetica-Bold',
                                       textColor=COLOR_MUTED, alignment=TA_RIGHT),
        
        'status_val': ParagraphStyle('status_val', fontSize=14, fontName='Helvetica-Bold',
                                     textColor=COLOR_SUCCESS_TEXT),
        'status_sub': ParagraphStyle('status_sub', fontSize=9, fontName='Helvetica-Bold',
                                     textColor=COLOR_PRIMARY, alignment=TA_RIGHT),
        'interpretation': ParagraphStyle('interpr', fontSize=8, fontName='Helvetica',
                                         textColor=COLOR_MUTED, alignment=TA_CENTER),
        
        'section_head': ParagraphStyle('sh', fontSize=9, fontName='Helvetica-Bold',
                                       textColor=COLOR_MUTED, spaceBefore=10, spaceAfter=4,
                                       textTransform='uppercase'),
        
        'label': ParagraphStyle('label', fontSize=8, fontName='Helvetica-Bold',
                                textColor=COLOR_MUTED, leading=10),
        'label_colored': ParagraphStyle('label_c', fontSize=8, fontName='Helvetica-Bold',
                                        textColor=COLOR_ORANGE, leading=10),
        'value': ParagraphStyle('value', fontSize=8, fontName='Helvetica',
                                textColor=COLOR_PRIMARY, leading=10),
        'value_bold': ParagraphStyle('val_b', fontSize=8, fontName='Helvetica-Bold',
                                     textColor=COLOR_PRIMARY, leading=10),
        
        'body': ParagraphStyle('body', fontSize=8.5, fontName='Helvetica',
                               textColor=COLOR_PRIMARY, leading=12),
        
        'footer_name': ParagraphStyle('fn', fontSize=9, fontName='Helvetica-Bold',
                                      textColor=COLOR_PRIMARY, alignment=TA_CENTER),
        'footer_sub': ParagraphStyle('fs', fontSize=7, fontName='Helvetica',
                                     textColor=COLOR_MUTED, alignment=TA_CENTER),
        'footer_label': ParagraphStyle('fl', fontSize=7, fontName='Helvetica',
                                       textColor=COLOR_MUTED, alignment=TA_CENTER),
        'legal': ParagraphStyle('legal', fontSize=6.5, fontName='Helvetica',
                                textColor=COLOR_MUTED, alignment=TA_CENTER),
    }

# ── Data Helpers ────────────────────────────────────────────

def _get_dosha_guidance(dosha: str):
    d = dosha.lower()
    guidance = {
        'vata': {
            'vikruti': "Imbalance in Vata energy (Air/Ether) causing dryness and coldness.",
            'precautions': [
                "Drink at least 3 liters of warm water daily for the next 5 days.",
                "Avoid heavy, oily, fried, or processed foods. Prefer light, cooked meals.",
                "Ensure 8 hours of uninterrupted sleep every night.",
                "Avoid vigorous physical activity; gentle yoga or walking is encouraged.",
                "Avoid exposure to cold wind, rain, or extreme temperature changes.",
                "Refrain from alcohol, tobacco, and caffeine for at least 5 days.",
                "Stay hydrated with herbal teas (ginger, tulsi) to aid detoxification."
            ],
            'herbs': [
                "Ashwagandha (Withania somnifera) - 500mg twice daily after meals",
                "Dashamoola Kwatha - 30ml morning on empty stomach",
                "Triphala Churna - 1 tsp at bedtime with warm water"
            ]
        },
        'pitta': {
            'vikruti': "Excessive heat affecting Pitta dosha.",
            'precautions': [
                "Drink at least 3 liters of warm water daily for the next 5 days.",
                "Avoid spicy, fried, and salty foods. Focus on cooling foods.",
                "Ensure 8 hours of uninterrupted sleep every night. Avoid late nights.",
                "Avoid vigorous physical activity; gentle yoga or walking is encouraged.",
                "Avoid direct sun exposure and high heat environments.",
                "Refrain from alcohol, tobacco, and caffeine for at least 5 days.",
                "Stay hydrated with herbal teas (mint, coriander) to aid detoxification."
            ],
            'herbs': [
                "Shatavari (Asparagus racemosus) - 500mg twice daily with milk",
                "Amalaki (Amla) powder - 1 tsp morning on empty stomach",
                "Kamadudha Ras - 1 tablet after meals for cooling",
                "Avipattikar Churna - 1 tsp before meals with warm water"
            ]
        },
        'kapha': {
            'vikruti': "Elevated Kapha leading to sluggishness and congestion.",
            'precautions': [
                "Drink at least 3 liters of warm water daily for the next 5 days.",
                "Avoid all dairy, sweets, and heavy fats. Prefer warm, light meals.",
                "Ensure 8 hours of uninterrupted sleep every night. No daytime sleeping.",
                "Engage in moderately vigorous physical activity for at least 30 mins.",
                "Keep the body warm and avoid damp environments.",
                "Refrain from alcohol, tobacco, and caffeine for at least 5 days.",
                "Stay hydrated with warm ginger water throughout the day."
            ],
            'herbs': [
                "Trikatu Churna - 500mg before meals with honey",
                "Guggulu (Commiphora mukul) - 500mg three times daily",
                "Punarnava - 30ml twice daily with warm water"
            ]
        }
    }
    for key in ('vata', 'pitta', 'kapha'):
        if key in d: return guidance[key]
    return guidance['vata']

# ── Main Generator ─────────────────────────────────────────

def generate_treatment_pdf(cycle):
    buffer = BytesIO()
    S = _get_styles()
    
    # Tight margins to fit 1 page
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=10*mm
    )
    story = []
    
    # ── Pulling Data ──
    patient = cycle.patient
    plan = cycle.treatment_plan
    attendances = list(cycle.attendances.all().order_by('date'))
    total_days = plan.duration_days if plan else 7
    attended_count = sum(1 for a in attendances if a.is_attended)
    attendance_pct = int((attended_count / total_days) * 100) if total_days else 0
    
    appt = patient.appointments.filter(status='completed').select_related('diagnosis_report').order_by('-date').first()
    diag_report = appt.diagnosis_report if appt and hasattr(appt, 'diagnosis_report') else None
    
    intake = {
        'age': str(appt.age) if appt else "—",
        'height': f"{appt.height} cm" if appt else "—",
        'weight': f"{appt.weight} kg" if appt else "—",
        'issues': appt.prior_health_issues if appt else "None reported",
        'vikruti': diag_report.diagnosis_result if diag_report else "Severe work needed in Pitta"
    }

    dosha = plan.target_dosha if plan else 'vata'
    guide = _get_dosha_guidance(dosha)
    case_id = f"PS-{cycle.id:05d}"
    
    # ── 1. HEADER ──────────────────────────────────────────
    # Logo + Title table
    logo_p = Paragraph('<font color="#10B981">Panchkarma</font><font color="#1F2937">Setu</font>', S['brand'])
    title_p = Paragraph("TREATMENT COMPLETION REPORT", S['header_right'])
    h_table = Table([[logo_p, title_p]], colWidths=[100*mm, 80*mm])
    h_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(h_table)
    story.append(Spacer(1, 2*mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_BRAND_GREEN, spaceAfter=6*mm))
    
    # ── 2. STATUS BLOCK ────────────────────────────────────
    # Dynamic Colors & Text based on attendance percentage
    if attendance_pct >= 70:
        st_bg, st_txt, st_brd = COLOR_SUCCESS_BG, COLOR_SUCCESS_TEXT, COLOR_SUCCESS_BRD
        status_text = "■ FULL SUCCESS" if attendance_pct == 100 else "■ TREATMENT SUCCESS"
        intep_text = "Excellent commitment. The treatment is expected to deliver full therapeutic benefit."
    elif attendance_pct >= 50:
        st_bg, st_txt, st_brd = COLOR_ORANGE_BG, COLOR_ORANGE, COLOR_ORANGE
        status_text = "■ PARTIAL SUCCESS"
        intep_text = "Good progress. Follow-up is essential to sustain results and complete the cycle."
    else:
        st_bg, st_txt, st_brd = colors.HexColor('#FEF2F2'), colors.HexColor('#B91C1C'), colors.HexColor('#EF4444')
        status_text = "■ TREATMENT INCOMPLETE"
        intep_text = "Significant interruption. Recommend restarting or intensifying follow-up to address imbalances."

    # Status value style override
    S['dynamic_status'] = ParagraphStyle('ds', parent=S['status_val'], textColor=st_txt)
    S['dynamic_intep']  = ParagraphStyle('di', parent=S['interpretation'], textColor=st_txt)

    status_msg = f"{attended_count} of {total_days} days attended ({attendance_pct}%)"
    st_inner_table = Table([[Paragraph(status_text, S['dynamic_status']), Paragraph(status_msg, S['status_sub'])]], colWidths=[100*mm, 70*mm])
    st_outer_table = Table([[st_inner_table]], colWidths=[W - 30*mm])
    st_outer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), st_bg),
        ('BOX', (0,0), (0,0), 0.8, st_brd),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (0,0), 8),
        ('TOPPADDING', (0,0), (0,0), 8),
    ]))
    story.append(st_outer_table)
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph(intep_text, S['dynamic_intep']))
    story.append(Spacer(1, 4*mm))

    # ── 3. ATTENDANCE LOG ──────────────────────────────────
    story.append(Paragraph("ATTENDANCE LOG", S['section_head']))
    log_data = []
    row = []
    for i in range(1, total_days + 1):
        is_done = False
        if i <= len(attendances): is_done = attendances[i-1].is_attended
        
        box_style = [
            ('BACKGROUND', (0,0), (0,0), COLOR_SUCCESS_BG if is_done else WHITE),
            ('TEXTCOLOR', (0,0), (0,0), COLOR_SUCCESS_TEXT if is_done else COLOR_MUTED),
            ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('VALIGN', (0,0), (0,0), 'MIDDLE'),
            ('BOX', (0,0), (0,0), 0.2, COLOR_BORDER),
        ]
        cell = Table([[str(i)]], colWidths=[20*mm], rowHeights=[6.5*mm])
        cell.setStyle(TableStyle(box_style))
        row.append(cell)
        if len(row) == 8:
            log_data.append(row)
            row = []
    if row:
        while len(row) < 8: row.append("")
        log_data.append(row)
        
    log_table = Table(log_data, colWidths=[21.25*mm]*8)
    log_table.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    story.append(log_table)
    story.append(Spacer(1, 4*mm))

    # ── 4. PATIENT INFORMATION ──────────────────────────────
    story.append(Paragraph("PATIENT INFORMATION", S['section_head']))
    
    def pi_row(l1, v1, l2, v2):
        return [
            Paragraph(l1, S['label']), Paragraph(str(v1), S['value']),
            Paragraph(l2, S['label']), Paragraph(str(v2), S['value'])
        ]
    
    pi_data = [
        pi_row('Username', patient.username, 'Age', intake['age']),
        pi_row('Height / Weight', f"{intake['height']} / {intake['weight']}", 'Email', patient.email),
        [Paragraph('Report Date', S['label']), Paragraph(date.today().strftime("%B %d, %Y"), S['value']), Paragraph('Prior Health Issues', S['label']), Paragraph(intake['issues'], S['value'])],
    ]
    pi_table = Table(pi_data, colWidths=[35*mm, 55*mm, 35*mm, 55*mm])
    pi_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (0,-1), COLOR_TABLE_BG),
        ('BACKGROUND', (2,0), (2,-1), COLOR_TABLE_BG),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(pi_table)
    story.append(Spacer(1, 4*mm))

    # ── 5. CLINICAL DIAGNOSIS ───────────────────────────────
    story.append(Paragraph("CLINICAL DIAGNOSIS: PRAKRITI & VIKRUTI", S['section_head']))
    diag_data = [
        [
            [Paragraph("Prakriti", S['label_colored']), Paragraph("(Natural Constitution)", S['label_colored'])],
            [Paragraph(f"Dominant Dosha: <b>{plan.get_target_dosha_display() if plan else 'Pitta'}</b>", S['body'])]
        ],
        [
            [Paragraph("Vikruti", S['label_colored']), Paragraph("(Current Imbalances)", S['label_colored'])],
            [Paragraph("<i>Findings:</i>", S['body']), Paragraph(intake['vikruti'], S['body'])]
        ]
    ]
    diag_table = Table(diag_data, colWidths=[40*mm, 140*mm])
    diag_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.8, COLOR_ORANGE),
        ('BACKGROUND', (0,0), (0,-1), COLOR_ORANGE_BG),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 4*mm))

    # ── 6. PRESCRIBED TREATMENT ─────────────────────────────
    story.append(Paragraph("PRESCRIBED TREATMENT", S['section_head']))
    pt_data = [
        pi_row('Plan Name', plan.name if plan else "—", 'Target Dosha', plan.get_target_dosha_display() if plan else "—"),
        pi_row('Duration', f"{total_days} days", 'Start Date', cycle.start_date.strftime("%B %d, %Y")),
        [Paragraph('Description', S['label']), Paragraph(plan.description if plan else "—", S['value']), '', '']
    ]
    pt_table = Table(pt_data, colWidths=[35*mm, 55*mm, 35*mm, 55*mm])
    pt_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (0,-1), COLOR_TABLE_BG),
        ('BACKGROUND', (2,0), (2,-1), COLOR_TABLE_BG),
        ('SPAN', (1,2), (3,2)),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(pt_table)
    story.append(Spacer(1, 4*mm))

    # ── 7. POST-TREATMENT PRECAUTIONS ───────────────────────
    story.append(Paragraph(f"POST-TREATMENT PRECAUTIONS (Next {5 if 'pitta' in dosha.lower() else 14} Days)", S['section_head']))
    for i, prec in enumerate(guide['precautions'], 1):
        story.append(Paragraph(f"<b>{i}.</b> {prec}", S['body']))
    story.append(Spacer(1, 4*mm))

    # ── 8. RECOMMENDED HERBAL SUPPLEMENTS ───────────────────
    story.append(Paragraph("RECOMMENDED HERBAL SUPPLEMENTS", S['section_head']))
    herb_list = [Paragraph(f"• {h}", S['body']) for h in guide['herbs']]
    h_box = Table([[herb_list]], colWidths=[W - 30*mm])
    h_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), COLOR_SUCCESS_BG),
        ('BOX', (0,0), (0,0), 0.8, COLOR_SUCCESS_BRD),
        ('BOTTOMPADDING', (0,0), (0,0), 8),
        ('TOPPADDING', (0,0), (0,0), 8),
    ]))
    story.append(h_box)
    
    # Push to bottom
    story.append(Spacer(1, 25*mm))

    # ── 9. FOOTER / AUTHENTICATION ─────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.2, color=COLOR_BORDER))
    story.append(Spacer(1, 4*mm))
    
    auth_data = [[
        [Paragraph(f"<b>{cycle.therapist.get_full_name() or 'dr_patil'}</b>", S['footer_name']),
         Paragraph("Certified Ayurvedic Therapist", S['footer_sub']),
         Spacer(1, 4*mm), HRFlowable(width="60%", thickness=0.5, color=COLOR_MUTED),
         Paragraph("Signature", S['footer_label'])],
        
        [Paragraph(f"<b>{patient.username}</b>", S['footer_name']),
         Paragraph("Patient", S['footer_sub']),
         Spacer(1, 4*mm), HRFlowable(width="60%", thickness=0.5, color=COLOR_MUTED),
         Paragraph("Acknowledged", S['footer_label'])],
        
        [Paragraph("<b>PanchkarmaSetu</b>", S['footer_name']),
         Paragraph("Wellness Platform", S['footer_sub']),
         Spacer(1, 4*mm), HRFlowable(width="60%", thickness=0.5, color=COLOR_MUTED),
         Paragraph("Authorized Seal", S['footer_label'])]
    ]]
    auth_table = Table(auth_data, colWidths=[(W-30*mm)/3]*3)
    auth_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(auth_table)
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("This document is an official treatment completion record generated by PanchkarmaSetu. Please retain this for your medical records.", S['legal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
