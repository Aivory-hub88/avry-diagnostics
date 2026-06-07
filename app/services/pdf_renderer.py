"""
PDF rendering service with Aivory branding and locked sections.
"""

import io
import base64
from pathlib import Path
from typing import List, Optional
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
    REPORTLAB_COLORS = colors
except ImportError:
    REPORTLAB_AVAILABLE = False
    REPORTLAB_COLORS = None
    print("Warning: ReportLab not installed. PDF generation will be limited.")


class PDFRenderingService:
    """
    Renders Blueprint PDF with Aivory branding and locked sections.
    
    PDF Structure:
    1. Header with logo and system name
    2. Executive Summary (full)
    3. System Overview Diagram (ASCII art)
    4. Agents & Roles (full list)
    5. Tools & Integrations (names only)
    6. Workflow Pseudo Code (1 full, rest locked)
    7. Deployment Estimate
    8. Footer with blueprint_id and schema_version
    """
    
    FONT_FAMILY = "Helvetica"  # Inter Tight not available in ReportLab, using Helvetica
    PRIMARY_COLOR = None  # Will be set in __init__
    LOCK_ICON = "🔒"
    
    def __init__(self):
        """Initialize PDF rendering service."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")
        
        # Set color after import check
        self.PRIMARY_COLOR = REPORTLAB_COLORS.HexColor("#7C3AED")  # Purple
        self.logo_path = Path("frontend/Aivory_logo.png")
    
    async def render_blueprint_pdf(
        self,
        blueprint_json: dict,
        user_email: str
    ) -> bytes:
        """
        Render Blueprint PDF with branding and locked sections.
        
        Args:
            blueprint_json: Complete Blueprint JSON data
            user_email: User email for header
            
        Returns:
            PDF as bytes
        """
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=self.PRIMARY_COLOR,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.PRIMARY_COLOR,
            spaceAfter=12,
            spaceBefore=20
        )
        
        # Header
        story.extend(self._render_header(blueprint_json, user_email, title_style, styles))
        
        # Executive Summary
        story.extend(self._render_executive_summary(blueprint_json, heading_style, styles))
        
        # System Overview
        story.extend(self._render_system_diagram(blueprint_json, heading_style, styles))
        
        # Agents & Roles
        story.extend(self._render_agents_section(blueprint_json, heading_style, styles))
        
        # Tools & Integrations
        story.extend(self._render_integrations_section(blueprint_json, heading_style, styles))
        
        # Workflow Pseudo Code (with locking)
        story.extend(self._render_workflow_pseudo_code(blueprint_json, heading_style, styles))
        
        # Deployment Estimate
        story.extend(self._render_deployment_estimate(blueprint_json, heading_style, styles))
        
        # Footer metadata
        story.extend(self._render_footer(blueprint_json, styles))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _render_header(self, blueprint_json: dict, user_email: str, title_style, styles) -> List:
        """Render header with logo and system name."""
        elements = []
        
        # Logo (if available)
        if self.logo_path.exists():
            try:
                from reportlab.platypus import Image
                logo = Image(str(self.logo_path), width=2*inch, height=0.5*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.3*inch))
            except:
                pass
        
        # Title
        elements.append(Paragraph("AI System Blueprint", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Metadata
        system_name = blueprint_json.get("system_name", "Unknown System")
        generated_at = blueprint_json.get("generated_at", datetime.utcnow().isoformat())
        
        # Convert datetime to string if needed
        if isinstance(generated_at, datetime):
            generated_at_str = generated_at.isoformat()[:10]
        else:
            generated_at_str = str(generated_at)[:10]
        
        meta_text = f"""
        <b>System:</b> {system_name}<br/>
        <b>Generated for:</b> {user_email}<br/>
        <b>Date:</b> {generated_at_str}
        """
        elements.append(Paragraph(meta_text, styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    def _render_executive_summary(self, blueprint_json: dict, heading_style, styles) -> List:
        """Generate and render executive summary."""
        elements = []
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
        
        system_name = blueprint_json.get("system_name", "AI System")
        num_agents = len(blueprint_json.get("agents", []))
        num_integrations = len(blueprint_json.get("integrations_required", []))
        estimate = blueprint_json.get("deployment_estimate", "40-60 hours")
        
        summary_text = f"""
        The <b>{system_name}</b> is a comprehensive AI automation solution designed to streamline 
        operations and enhance efficiency. This blueprint outlines a system comprising <b>{num_agents} intelligent agents</b> 
        working in concert to automate key business processes.
        <br/><br/>
        The system requires integration with <b>{num_integrations} external services</b> and is estimated to take 
        <b>{estimate}</b> to fully deploy. This blueprint provides detailed specifications for each agent, 
        workflow logic, and integration requirements to enable rapid implementation.
        """
        
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _render_system_diagram(self, blueprint_json: dict, heading_style, styles) -> List:
        """Render ASCII flow diagram showing agent connections."""
        elements = []
        
        elements.append(Paragraph("SYSTEM OVERVIEW", heading_style))
        
        agents = blueprint_json.get("agents", [])
        
        # Simple ASCII diagram
        diagram_text = "<font name='Courier' size='10'>"
        diagram_text += "User Input<br/>"
        diagram_text += "    ↓<br/>"
        
        for idx, agent in enumerate(agents):
            agent_name = agent.get("name", f"Agent {idx+1}")
            diagram_text += f"{agent_name}<br/>"
            if idx < len(agents) - 1:
                diagram_text += "    ↓<br/>"
        
        diagram_text += "    ↓<br/>"
        diagram_text += "Output / Action"
        diagram_text += "</font>"
        
        elements.append(Paragraph(diagram_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _render_agents_section(self, blueprint_json: dict, heading_style, styles) -> List:
        """Render full agent list with roles."""
        elements = []
        
        elements.append(Paragraph("AGENTS & ROLES", heading_style))
        
        agents = blueprint_json.get("agents", [])
        
        for idx, agent in enumerate(agents, 1):
            agent_name = agent.get("name", f"Agent {idx}")
            trigger = agent.get("trigger", "manual")
            tools = agent.get("tools", [])
            
            agent_text = f"""
            <b>{idx}. {agent_name}</b><br/>
            <i>Trigger:</i> {trigger}<br/>
            <i>Tools:</i> {', '.join(tools)}<br/>
            """
            
            elements.append(Paragraph(agent_text, styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _render_integrations_section(self, blueprint_json: dict, heading_style, styles) -> List:
        """Render integration names (high-level only)."""
        elements = []
        
        elements.append(Paragraph("TOOLS & INTEGRATIONS", heading_style))
        
        integrations = blueprint_json.get("integrations_required", [])
        
        if integrations:
            integration_list = "<br/>".join([
                f"• {integration.get('service_name', 'Unknown Service')}"
                for integration in integrations
            ])
            elements.append(Paragraph(integration_list, styles['Normal']))
        else:
            elements.append(Paragraph("No external integrations required.", styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _render_workflow_pseudo_code(self, blueprint_json: dict, heading_style, styles) -> List:
        """
        Render workflow pseudo code with locking.
        
        Logic:
        - Show full pseudo_logic for agents[0]
        - For agents[1:], show lock icon and message
        """
        elements = []
        
        elements.append(Paragraph("WORKFLOW PSEUDO CODE", heading_style))
        
        agents = blueprint_json.get("agents", [])
        
        if agents:
            # Show first agent in full
            first_agent = agents[0]
            agent_name = first_agent.get("name", "Agent 1")
            pseudo_logic = first_agent.get("pseudo_logic", [])
            
            agent_text = f"<b>{agent_name}:</b><br/>"
            for logic in pseudo_logic:
                agent_text += f"  {logic}<br/>"
            
            elements.append(Paragraph(agent_text, styles['Code']))
            elements.append(Spacer(1, 0.2*inch))
            
            # Lock remaining agents
            if len(agents) > 1:
                for agent in agents[1:]:
                    agent_name = agent.get("name", "Agent")
                    locked_text = f"<b>{agent_name}:</b> {self.LOCK_ICON} LOCKED"
                    elements.append(Paragraph(locked_text, styles['Normal']))
                    elements.append(Spacer(1, 0.1*inch))
                
                unlock_message = """
                <i>Full workflow details available in dashboard and Step 3 subscription</i>
                """
                elements.append(Paragraph(unlock_message, styles['Italic']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _render_deployment_estimate(self, blueprint_json: dict, heading_style, styles) -> List:
        """Render deployment estimate."""
        elements = []
        
        estimate = blueprint_json.get("deployment_estimate", "40-60 hours")
        
        estimate_text = f"<b>DEPLOYMENT ESTIMATE:</b> {estimate}"
        elements.append(Paragraph(estimate_text, heading_style))
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _render_footer(self, blueprint_json: dict, styles) -> List:
        """Render footer with metadata and branding."""
        elements = []
        
        blueprint_id = blueprint_json.get("blueprint_id", "unknown")
        schema_version = blueprint_json.get("schema_version", "aivory-v1")
        
        footer_text = f"""
        <br/><br/>
        ─────────────────────────────────────────────────────────<br/>
        <b>Blueprint ID:</b> {blueprint_id}<br/>
        <b>Schema Version:</b> {schema_version}<br/>
        <br/>
        <b>Aivory</b> | contact@aivory.id | aivory.id
        """
        
        elements.append(Paragraph(footer_text, styles['Normal']))
        
        return elements


# Fallback simple PDF generator if ReportLab not available
class SimplePDFGenerator:
    """Simple text-based PDF generator as fallback."""
    
    async def render_blueprint_pdf(self, blueprint_json: dict, user_email: str) -> bytes:
        """Generate simple text-based PDF."""
        # This would need a different library or just return text
        text_content = f"""
AI SYSTEM BLUEPRINT

System: {blueprint_json.get('system_name', 'Unknown')}
Generated for: {user_email}
Blueprint ID: {blueprint_json.get('blueprint_id', 'unknown')}

This is a simplified PDF. Install ReportLab for full PDF generation:
pip install reportlab
"""
        return text_content.encode('utf-8')
