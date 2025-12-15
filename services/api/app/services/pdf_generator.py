from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
import os
from datetime import datetime
from typing import Dict, Any, List

class PDFGenerator:
    def __init__(self):
        self.brand_color = colors.HexColor('#0F172A') # Slate 900
        self.accent_color = colors.HexColor('#2563EB') # Blue 600
        self.warning_color = colors.HexColor('#F59E0B') # Amber 500
        self.error_color = colors.HexColor('#EF4444') # Red 500
        self.success_color = colors.HexColor('#10B981') # Emerald 500

    def generate_client_blueprint(self, audit_data: Dict[str, Any], output_path: str = None) -> bytes:
        """Generate the client-facing Blueprint PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=50, leftMargin=50,
            topMargin=50, bottomMargin=50
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=self.brand_color,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.accent_color,
            spaceBefore=20,
            spaceAfter=10
        )
        
        body_style = styles['Normal']
        body_style.spaceAfter = 12
        
        # --- HEADER ---
        elements.append(Paragraph("CREDIT REPAIR BLUEPRINT", title_style))
        elements.append(Paragraph(f"Prepared for: {audit_data.get('clientName', 'Valued Client')}", 
                                ParagraphStyle('SubTitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14)))
        elements.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", 
                                ParagraphStyle('Date', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, textColor=colors.gray)))
        elements.append(Spacer(1, 40))
        
        # --- EXECUTIVE SUMMARY ---
        elements.append(Paragraph("Executive Summary", heading_style))
        scores = audit_data.get('scores', {})
        
        summary_data = [
            ['Bureau', 'Score', 'Status'],
            ['TransUnion', str(scores.get('transunion') or 'N/A'), self._get_score_status(scores.get('transunion'))],
            ['Equifax', str(scores.get('equifax') or 'N/A'), self._get_score_status(scores.get('equifax'))],
            ['Experian', str(scores.get('experian') or 'N/A'), self._get_score_status(scores.get('experian'))]
        ]
        
        t = Table(summary_data, colWidths=[200, 100, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0'))
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        # --- CRITICAL ISSUES ---
        elements.append(Paragraph("Critical Issues Identified", heading_style))
        
        summary = audit_data.get('summary', {})
        issues = []
        if summary.get('totalViolationsFound', 0) > 0:
            issues.append(f"• Found {summary.get('totalViolationsFound')} potential FCRA violations")
        if summary.get('utilizationPercentage', 0) > 30:
            issues.append(f"• High Credit Utilization: {summary.get('utilizationPercentage')}% (Target: <10%)")
        if summary.get('totalCollections', 0) > 0:
            issues.append(f"• Found {summary.get('totalCollections')} collection accounts")
        if summary.get('needsStarterAccounts'):
            issues.append("• Thin credit file - Need to add positive tradelines")
            
        for issue in issues:
            elements.append(Paragraph(issue, body_style))
            
        elements.append(Spacer(1, 20))
        
        # --- ACTION PLAN / RECOMMENDATIONS ---
        elements.append(Paragraph("Your Strategic Action Plan", heading_style))
        
        recommendations = audit_data.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
             # Title with Priority Color
            prio_color = self.brand_color
            if rec.get('priority') == 1: prio_color = self.error_color
            if rec.get('priority') == 2: prio_color = self.warning_color
            
            elements.append(Paragraph(f"{i}. {rec.get('title')}", 
                                    ParagraphStyle('RecTitle', parent=styles['Heading3'], textColor=prio_color)))
            elements.append(Paragraph(rec.get('description', ''), body_style))
            if rec.get('estimatedImpact'):
                 elements.append(Paragraph(f"<b>Estimated Impact:</b> {rec.get('estimatedImpact')}", 
                                         ParagraphStyle('Impact', parent=body_style, textColor=self.success_color)))
            items = []
            if rec.get('productUrl'):
                link = f'<a href="{rec.get("productUrl")}" color="blue">{rec.get("productName", "Click here to apply")}</a>'
                elements.append(Paragraph(f"Recommended Action: {link}", body_style))
            
            elements.append(Spacer(1, 10))

        # --- NEXT STEPS ---
        elements.append(PageBreak())
        elements.append(Paragraph("Next Steps", heading_style))
        elements.append(Paragraph("1. Review this blueprint carefully.", body_style))
        elements.append(Paragraph("2. Sign the service agreement to begin the dispute process.", body_style))
        elements.append(Paragraph("3. Implement the positive credit building recommendations above.", body_style))
        elements.append(Paragraph("4. Upload requested documents (ID, Utility Bill) to your portal.", body_style))
        
        # BUILD
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes

    def generate_internal_blueprint(self, audit_data: Dict[str, Any]) -> bytes:
        """Generate internal company audit PDF with more technical details"""
        # Ideally this reuses logic but adds more data sections like specific violation codes
        # For simplicity, we'll return the same structure but with added 'Internal' flag context if needed
        # Or just append the internal details.
        
        # Just wrapping the client one for now but typically would have the full item breakdown
        # Let's add the detailed Item Review here
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph("INTERNAL AUDIT REPORT", styles['Title']))
        elements.append(Paragraph(f"Client: {audit_data.get('clientName')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Items Table
        items = audit_data.get('itemsForReview', [])
        if items:
            elements.append(Paragraph("Audit Items Detail", styles['Heading2']))
            
            table_data = [['Account', 'Type', 'Violations', 'Resolution']]
            for item in items:
                table_data.append([
                    item.get('creditorName', 'N/A')[:20],
                    item.get('itemType', 'N/A'),
                    str(item.get('violationCount', 0)),
                    item.get('suggestedResolution', 'N/A')
                ])
                
            t = Table(table_data, colWidths=[150, 100, 80, 150])
            t.setStyle(TableStyle([
                 ('GRID', (0, 0), (-1, -1), 1, colors.black),
                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ]))
            elements.append(t)
            
        doc.build(elements)
        return buffer.getvalue()

    def _get_score_status(self, score):
        if not score: return "N/A"
        try:
            val = int(score)
            if val >= 750: return "Excellent"
            if val >= 700: return "Good"
            if val >= 650: return "Fair"
            if val >= 600: return "Needs Work"
            return "Poor"
        except:
            return "N/A"

pdf_generator = PDFGenerator()
