# ==========================================
# GÉNÉRATEUR PDF : MODULE RAPPORTS
# Utilise ReportLab pour créer les rapports
# ==========================================

import io
from datetime import date
from django.db.models import Q
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from django.db.models import Count
from signalements.models import Signalement, CategorieProbleme
from localisation.models import Commune


# Palette de couleurs UrbanAlert
VERT_URBANALERT = colors.HexColor('#2ecc71')
VERT_FONCE = colors.HexColor('#27ae60')
GRIS_CLAIR = colors.HexColor('#ecf0f1')
GRIS_MOYEN = colors.HexColor('#bdc3c7')
TEXTE_SOMBRE = colors.HexColor('#2c3e50')
ROUGE = colors.HexColor('#e74c3c')
ORANGE = colors.HexColor('#f39c12')


def generer_pdf_rapport(type_rapport: str, debut: date, fin: date) -> bytes:
    """
    Génère le contenu binaire d'un rapport PDF UrbanAlert.

    Args:
        type_rapport: 'hebdomadaire' ou 'mensuel'
        debut: date de début de la période
        fin: date de fin de la période

    Returns:
        bytes : contenu du PDF
    """

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    # --- Styles personnalisés ---
    style_titre = ParagraphStyle(
        'TitreUA',
        parent=styles['Title'],
        fontSize=22,
        textColor=VERT_FONCE,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    style_sous_titre = ParagraphStyle(
        'SousTitreUA',
        parent=styles['Normal'],
        fontSize=12,
        textColor=TEXTE_SOMBRE,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    style_section = ParagraphStyle(
        'SectionUA',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=VERT_FONCE,
        spaceBefore=14,
        spaceAfter=6,
        borderPad=4,
    )
    style_normal = ParagraphStyle(
        'NormalUA',
        parent=styles['Normal'],
        fontSize=10,
        textColor=TEXTE_SOMBRE,
    )

    elements = []

    # ======================
    # EN-TÊTE DU RAPPORT
    # ======================

    elements.append(Paragraph("UrbanAlert", style_titre))
    elements.append(Paragraph(
        f"Rapport {type_rapport.capitalize()} — "
        f"Du {debut.strftime('%d/%m/%Y')} au {fin.strftime('%d/%m/%Y')}",
        style_sous_titre
    ))
    elements.append(Paragraph(
        f"Généré le {date.today().strftime('%d/%m/%Y')} | "
        "Système de Signalement des Problèmes Urbains de Conakry",
        style_sous_titre
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=VERT_URBANALERT))
    elements.append(Spacer(1, 0.4 * cm))

    # ======================
    # DONNÉES DE LA PÉRIODE
    # ======================

    signalements_periode = Signalement.objects.filter(
        date_creation__date__gte=debut,
        date_creation__date__lte=fin
    )

    total = signalements_periode.count()
    en_attente = signalements_periode.filter(statut__code='en_attente').count()
    en_cours = signalements_periode.filter(statut__code='en_cours').count()
    resolus = signalements_periode.filter(statut__code='resolu').count()
    rejetes = signalements_periode.filter(statut__code='rejete').count()
    urgences = signalements_periode.filter(est_urgence=True).count()

    taux = round((resolus / total * 100) if total > 0 else 0, 1)

    # ======================
    # SECTION 1 : RÉSUMÉ
    # ======================

    elements.append(Paragraph("1. Résumé de la période", style_section))

    resume_data = [
        ['Indicateur', 'Valeur'],
        ['Total de signalements', str(total)],
        ['En attente', str(en_attente)],
        ['En cours de traitement', str(en_cours)],
        ['Résolus', str(resolus)],
        ['Rejetés', str(rejetes)],
        ['Signalements d\'urgence', str(urgences)],
        ['Taux de résolution', f"{taux} %"],
    ]

    table_resume = Table(resume_data, colWidths=[10 * cm, 6 * cm])
    table_resume.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), VERT_FONCE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GRIS_CLAIR]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, GRIS_MOYEN),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table_resume)
    elements.append(Spacer(1, 0.4 * cm))

    # ======================
    # SECTION 2 : PAR CATÉGORIE
    # ======================

    elements.append(Paragraph("2. Signalements par catégorie", style_section))

    par_cat = (
        CategorieProbleme.objects
        .annotate(nb=Count(
            'sous_categories__signalements',
            filter=Q(
                sous_categories__signalements__date_creation__date__gte=debut,
                sous_categories__signalements__date_creation__date__lte=fin
            )
        ))
        .order_by('-nb')
    )

    cat_data = [['Catégorie', 'Nombre de signalements', 'Pourcentage']]
    for cat in par_cat:
        pct = round((cat.nb / total * 100) if total > 0 else 0, 1)
        cat_data.append([cat.nom, str(cat.nb), f"{pct} %"])

    table_cat = Table(cat_data, colWidths=[9 * cm, 4 * cm, 3 * cm])
    table_cat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), VERT_FONCE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GRIS_CLAIR]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, GRIS_MOYEN),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table_cat)
    elements.append(Spacer(1, 0.4 * cm))

    # ======================
    # SECTION 3 : PAR COMMUNE
    # ======================

    elements.append(Paragraph("3. Signalements par commune", style_section))

    par_com = (
        Commune.objects
        .annotate(nb=Count(
            'quartiers__signalements',
            filter=Q(
                quartiers__signalements__date_creation__date__gte=debut,
                quartiers__signalements__date_creation__date__lte=fin
            )
        ))
        .order_by('-nb')
    )

    com_data = [['Commune', 'Signalements', 'Résolus']]
    for com in par_com:
        nb_resolus_com = signalements_periode.filter(
            quartier__commune=com,
            statut__code='resolu'
        ).count()
        com_data.append([com.nom, str(com.nb), str(nb_resolus_com)])

    table_com = Table(com_data, colWidths=[9 * cm, 4 * cm, 3 * cm])
    table_com.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), VERT_FONCE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GRIS_CLAIR]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, GRIS_MOYEN),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table_com)
    elements.append(Spacer(1, 0.4 * cm))

    # ======================
    # SECTION 4 : TOP SIGNALEMENTS
    # ======================

    elements.append(Paragraph("4. Top 10 signalements les plus votés", style_section))

    top = (
        signalements_periode
        .annotate(nb_votes=Count('votes'))
        .order_by('-nb_votes')[:10]
    )

    top_data = [['#', 'Titre', 'Commune', 'Statut', 'Votes']]
    for i, s in enumerate(top, 1):
        top_data.append([
            str(i),
            s.titre[:45] + ('…' if len(s.titre) > 45 else ''),
            s.quartier.commune.nom,
            s.statut.nom_statut,
            str(s.nb_votes),
        ])

    table_top = Table(top_data, colWidths=[1 * cm, 7.5 * cm, 3 * cm, 3 * cm, 1.5 * cm])
    table_top.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), VERT_FONCE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (4, 0), (4, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GRIS_CLAIR]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, GRIS_MOYEN),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(table_top)
    elements.append(Spacer(1, 0.6 * cm))

    # ======================
    # PIED DE PAGE
    # ======================

    elements.append(HRFlowable(width="100%", thickness=1, color=GRIS_MOYEN))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(
        "UrbanAlert — Université Kofi Annan de Guinée | Rapport généré automatiquement",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8,
                       textColor=GRIS_MOYEN, alignment=TA_CENTER)
    ))

    # ======================
    # COMPILATION DU PDF
    # ======================

    doc.build(elements)
    return buffer.getvalue()
