"""
Diagnostic Export Service
Handles PDF and image export for diagnostic results.
"""

import io
import base64
from typing import Optional, Dict, Any
from datetime import datetime


class DiagnosticExportService:
    """Service for exporting diagnostic results to various formats"""
    
    @staticmethod
    def generate_pdf_html(diagnostic: Dict[str, Any]) -> str:
        """
        Generate HTML for PDF export of diagnostic results.
        
        Args:
            diagnostic: Diagnostic record dict
            
        Returns:
            HTML string for PDF rendering
        """
        score = diagnostic.get("score", 0)
        category = diagnostic.get("category", "")
        category_explanation = diagnostic.get("category_explanation", "")
        insights = diagnostic.get("insights", [])
        recommendations = diagnostic.get("recommendations", [])
        company_name = diagnostic.get("company_name", "Company")
        created_at = diagnostic.get("created_at", "")
        
        # Format created_at
        if created_at:
            try:
                dt = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
                created_at_str = dt.strftime("%B %d, %Y")
            except:
                created_at_str = str(created_at)
        else:
            created_at_str = datetime.now().strftime("%B %d, %Y")
        
        # Color based on category
        color_map = {
            "Advanced": "#10b981",  # green
            "Established": "#3b82f6",  # blue
            "Emerging": "#f59e0b",  # amber
            "Foundational": "#ef4444"  # red
        }
        color = color_map.get(category, "#6b7280")
        
        # Build insights HTML
        insights_html = ""
        for i, insight in enumerate(insights, 1):
            insights_html += f"""
            <li style="margin-bottom: 10px; line-height: 1.6;">
                <strong>Insight {i}:</strong> {insight}
            </li>
            """
        
        # Build recommendations HTML
        recommendations_html = ""
        for i, rec in enumerate(recommendations, 1):
            recommendations_html += f"""
            <li style="margin-bottom: 10px; line-height: 1.6;">
                <strong>Action {i}:</strong> {rec}
            </li>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>AI Readiness Diagnostic Report</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #1f2937;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 40px;
                    background: #f9fafb;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                    border-bottom: 3px solid {color};
                    padding-bottom: 20px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #111827;
                    margin-bottom: 10px;
                }}
                .report-date {{
                    color: #6b7280;
                    font-size: 14px;
                }}
                .company {{
                    font-size: 20px;
                    color: #374151;
                    margin-top: 10px;
                }}
                .score-section {{
                    background: white;
                    border: 2px solid {color};
                    border-radius: 12px;
                    padding: 30px;
                    margin: 30px 0;
                    text-align: center;
                }}
                .score-display {{
                    font-size: 60px;
                    font-weight: 700;
                    color: {color};
                    margin: 20px 0;
                }}
                .category {{
                    font-size: 28px;
                    font-weight: 600;
                    color: {color};
                    margin: 10px 0;
                }}
                .category-explanation {{
                    color: #6b7280;
                    margin-top: 15px;
                    line-height: 1.8;
                    font-style: italic;
                }}
                .section {{
                    background: white;
                    padding: 25px;
                    margin: 25px 0;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .section-title {{
                    font-size: 18px;
                    font-weight: 700;
                    color: #111827;
                    margin-bottom: 15px;
                    border-left: 4px solid {color};
                    padding-left: 15px;
                }}
                ul {{
                    list-style: none;
                    padding: 0;
                }}
                li {{
                    margin-bottom: 12px;
                }}
                .footer {{
                    text-align: center;
                    color: #9ca3af;
                    font-size: 12px;
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                }}
                .metadata {{
                    display: flex;
                    justify-content: space-between;
                    margin-top: 20px;
                    font-size: 14px;
                    color: #6b7280;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">🤖 Aivory</div>
                <div class="logo" style="font-size: 16px; font-weight: 400;">AI Readiness Diagnostic Report</div>
                <div class="report-date">Generated on {created_at_str}</div>
                <div class="company">{company_name}</div>
            </div>
            
            <div class="score-section">
                <div style="color: #6b7280;">Your AI Readiness Score</div>
                <div class="score-display">{score}/100</div>
                <div class="category">{category}</div>
                <div class="category-explanation">
                    {category_explanation}
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Key Insights</div>
                <ul>
                    {insights_html}
                </ul>
            </div>
            
            <div class="section">
                <div class="section-title">Recommended Actions</div>
                <ul>
                    {recommendations_html}
                </ul>
            </div>
            
            <div class="footer">
                <p>This report was generated by Aivory AI Readiness Platform.<br>
                For more information or to upgrade your subscription, visit aivory.id</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def generate_email_html(diagnostic: Dict[str, Any], share_url: str) -> str:
        """
        Generate HTML for email sharing of diagnostic results.
        
        Args:
            diagnostic: Diagnostic record dict
            share_url: URL to view shared results
            
        Returns:
            HTML email template
        """
        score = diagnostic.get("score", 0)
        category = diagnostic.get("category", "")
        company_name = diagnostic.get("company_name", "Company")
        
        # Category colors and emojis
        category_map = {
            "Advanced": ("🚀", "#10b981"),
            "Established": ("📈", "#3b82f6"),
            "Emerging": ("🌱", "#f59e0b"),
            "Foundational": ("🔧", "#ef4444")
        }
        
        emoji, color = category_map.get(category, ("📊", "#6b7280"))
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Aivory AI Readiness Diagnostic Results</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">🤖 Aivory</h1>
                    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">AI Readiness Diagnostic Results</p>
                </div>
                
                <!-- Main Content -->
                <div style="background: white; border: 1px solid #e5e7eb; border-top: none; padding: 40px;">
                    <p style="margin: 0 0 20px 0; font-size: 16px;">
                        Hi {company_name},
                    </p>
                    
                    <p style="margin: 0 0 30px 0; color: #6b7280;">
                        Your AI Readiness Diagnostic assessment is complete! Here's your summary:
                    </p>
                    
                    <!-- Score Card -->
                    <div style="background: #{color.lstrip('#')}11; border: 2px solid {color}; border-radius: 8px; padding: 25px; text-align: center; margin: 30px 0;">
                        <div style="font-size: 14px; color: #6b7280; margin-bottom: 10px;">Your Score</div>
                        <div style="font-size: 48px; font-weight: 700; color: {color}; margin: 10px 0;">{score}/100</div>
                        <div style="font-size: 18px; font-weight: 600; color: {color};">{emoji} {category}</div>
                    </div>
                    
                    <p style="margin: 30px 0; color: #6b7280;">
                        Your assessment reveals your current AI maturity level and provides actionable recommendations for your organization.
                    </p>
                    
                    <!-- CTA Button -->
                    <div style="text-align: center; margin: 40px 0;">
                        <a href="{share_url}" style="background: #667eea; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block;">
                            View Full Report
                        </a>
                    </div>
                    
                    <!-- Features -->
                    <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin: 30px 0;">
                        <p style="margin: 0 0 15px 0; font-weight: 600; color: #111827;">In Your Report:</p>
                        <ul style="margin: 0; padding-left: 20px; color: #6b7280;">
                            <li style="margin-bottom: 8px;">✓ Detailed score breakdown by category</li>
                            <li style="margin-bottom: 8px;">✓ Personalized insights about your organization</li>
                            <li style="margin-bottom: 8px;">✓ Actionable recommendations</li>
                            <li>✓ Shareable results with your team</li>
                        </ul>
                    </div>
                    
                    <!-- Next Steps -->
                    <div style="margin: 30px 0;">
                        <p style="margin: 0 0 15px 0; font-weight: 600; color: #111827;">Next Steps:</p>
                        <p style="margin: 0; color: #6b7280;">
                            Share this assessment with your team and discuss how your organization can improve its AI readiness. 
                            Consider upgrading to access deeper analysis and more comprehensive recommendations.
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background: #f3f4f6; padding: 30px; border-radius: 0 0 12px 12px; text-align: center; font-size: 12px; color: #9ca3af; border: 1px solid #e5e7eb; border-top: none;">
                    <p style="margin: 0 0 10px 0;">
                        <a href="https://aivory.id" style="color: #667eea; text-decoration: none;">Visit Aivory</a> |
                        <a href="https://aivory.id/help" style="color: #667eea; text-decoration: none; margin-left: 10px;">Support</a>
                    </p>
                    <p style="margin: 0;">
                        © 2024 Aivory. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def generate_csv_export(diagnostics: list[Dict[str, Any]]) -> str:
        """
        Generate CSV export of diagnostics.
        
        Args:
            diagnostics: List of diagnostic records
            
        Returns:
            CSV string
        """
        csv_lines = [
            "ID,User ID,Company,Score,Category,View Count,Public,Created At"
        ]
        
        for diag in diagnostics:
            company = diag.get("company_name", "").replace(",", ";")
            csv_lines.append(
                f"{diag.get('id')},{diag.get('user_id', '')},\"{company}\","
                f"{diag.get('score', 0)},{diag.get('category', '')},{diag.get('view_count', 0)},"
                f"{diag.get('is_public', False)},{diag.get('created_at', '')}"
            )
        
        return "\n".join(csv_lines)
