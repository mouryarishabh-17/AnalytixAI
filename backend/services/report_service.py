
from fpdf import FPDF
import os
from datetime import datetime

class pdf(FPDF):
    def header(self):
        # Logo could go here
        self.set_font('Arial', 'B', 12)
        self.set_text_color(100, 100, 150)
        self.cell(0, 10, 'AnalytixAI Automated Report', 0, 1, 'R')
        self.ln(5)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

class ReportService:
    @staticmethod
    def _clean_text(text):
        """Sanitize text for PDF (latin-1)"""
        if not isinstance(text, str):
            text = str(text)
        # Replace common unicode chars causing issues
        replacements = {
            '•': '-', '—': '-', '–': '-', 
            '’': "'", '‘': "'", 
            '“': '"', '”': '"',
            '…': '...'
        }
        for char, repl in replacements.items():
            text = text.replace(char, repl)
            
        return text.encode('latin-1', 'replace').decode('latin-1')

    @staticmethod
    def generate_pdf(data, charts, session_id, output_filename=None):
        try:
            print(f"📄 Starting PDF Generation for {session_id}")
            doc = pdf()
            doc.set_auto_page_break(auto=True, margin=15)
            doc.add_page()
            
            # --- TITLE PAGE ---
            print("  - Adding Title Page")
            doc.set_font("Arial", 'B', 24)
            doc.set_text_color(44, 62, 80) # Dark Blue
            doc.cell(0, 20, txt=f"{data.get('domain', 'Data').title()} Analysis Report", ln=True, align='C')
            
            doc.set_font("Arial", size=10)
            doc.set_text_color(100)
            doc.cell(0, 10, txt=f"Filename: {data.get('filename', 'Unknown')}", ln=True, align='C')
            
            # Add Generation Timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            doc.cell(0, 10, txt=f"Generated on: {current_time}", ln=True, align='C')
            doc.ln(10)
            doc.set_text_color(0)

            analytics = data.get('analytics', {})
            ml = analytics.get('ml_insights', {})

            # --- EXECUTIVE SUMMARY ---
            print("  - Adding Executive Summary")
            doc.set_font("Arial", 'B', 16)
            doc.set_fill_color(240, 240, 240)
            doc.cell(0, 10, txt="  Executive Summary", ln=True, fill=True)
            doc.ln(5)
            
            doc.set_font("Arial", size=11)
            # ML Summary
            summary_text = ReportService._clean_text(ml.get('summary', 'Standard analysis completed.'))
            doc.multi_cell(0, 7, txt=summary_text)
            doc.ln(8)

            # --- KEY STATISTICS (GRID LAYOUT) ---
            print("  - Adding Key Statistics")
            if analytics.get('summary_stats'):
                doc.set_font("Arial", 'B', 14)
                doc.cell(0, 10, txt="Key Statistics", ln=True)
                doc.set_font("Arial", size=10)
                
                stats = analytics['summary_stats'].get('metrics', {}) # fallback
                if not stats and 'summary_stats' in analytics: 
                     flat_stats = {}
                     for k,v in analytics['summary_stats'].items():
                         if isinstance(v, (int, float, str)): flat_stats[k] = v
                         elif isinstance(v, dict): 
                             for sk, sv in v.items(): flat_stats[f"{k} {sk}"] = sv
                     stats = flat_stats

                # Grid Layout (2 Columns)
                col_width = 85
                row_height = 8
                i = 0
                
                if stats:
                    for k, v in list(stats.items())[:14]: # Limit items
                        clean_k = ReportService._clean_text(str(k)).replace('_', ' ').title()
                        clean_v = ReportService._clean_text(str(v))
                        
                        # Truncate
                        label = f"{clean_k}: {clean_v}"
                        if len(label) > 45: label = label[:42] + "..."
                        
                        doc.cell(col_width, row_height, txt=f" {label}", border=1)
                        
                        if (i + 1) % 2 == 0:
                            doc.ln() # New line after 2 items
                        i += 1
                    
                    if i % 2 != 0: doc.ln() # Close row if odd
                    doc.ln(10)

            # --- PREDICTIVE ANALYSIS (NEW) ---
            print("  - Adding Predictive Analysis")
            if ml and ml.get('status') != 'data_issue':
                doc.add_page()
                doc.set_font("Arial", 'B', 16)
                doc.set_fill_color(230, 240, 255) # Light Blue header
                doc.cell(0, 10, txt="  AI Predictive Analysis", ln=True, fill=True)
                doc.ln(5)
                
                # Accuracy / Confidence
                if ml.get('accuracy'):
                    doc.set_font("Arial", 'B', 12)
                    doc.cell(0, 10, txt=f"Model Confidence: {ml.get('accuracy')}", ln=True)

                # Drivers
                drivers = ml.get('top_drivers', [])
                if drivers:
                    doc.set_font("Arial", 'B', 14)
                    doc.cell(0, 10, txt="Key Drivers (What impacts results?)", ln=True)
                    doc.set_font("Arial", size=11)
                    doc.ln(2)
                    
                    for d in drivers:
                        feat = ReportService._clean_text(d.get('feature', 'Unknown'))
                        imp = d.get('importance', 0)
                        
                        # Visualize magnitude with text bar
                        bar_len = int(imp / 4) # scale
                        if bar_len < 1: bar_len = 1
                        bar = "|" * bar_len
                        
                        doc.set_font("Courier", size=10) # Monospace for alignment
                        doc.cell(10, 6, txt=f"{int(imp)}% ", align='R')
                        doc.set_font("Arial", 'B', 11)
                        doc.cell(0, 6, txt=f" {feat}", ln=True)
                        doc.ln(2)

            # --- KEY INSIGHTS ---
            print("  - Adding Key Insights")
            insights = analytics.get('key_insights', [])
            if insights:
                doc.add_page()
                doc.set_font("Arial", 'B', 16)
                doc.cell(0, 10, txt="Key Insights", ln=True)
                doc.ln(5)
                doc.set_font("Arial", size=11)
                
                for ins in insights:
                    title = ReportService._clean_text(ins.get('title', 'Insight'))
                    obs = ReportService._clean_text(ins.get('observation', ''))
                    
                    doc.set_font("Arial", 'B', 12)
                    doc.set_text_color(0, 102, 204) # Blue title
                    doc.cell(0, 8, txt=f"- {title}", ln=True)
                    doc.set_text_color(0)
                    doc.multi_cell(0, 6, txt=f"  {obs}")
                    doc.ln(4)

            # --- VISUALS ---
            print("  - Adding Visuals")
            if charts:
                doc.add_page()
                doc.set_font("Arial", 'B', 16)
                doc.cell(0, 10, txt="Visual Analysis", ln=True)
                doc.ln(5)
                
                for name, path in charts.items():
                    # clean path (absolute paths passed from main.py, or relative from legacy)
                    # Safe to use lstrip('/') for sanity if it was a URL path, but os.path.join handled defaults.
                    local_path = path.lstrip('/')
                    
                    if os.path.exists(local_path):
                        doc.set_font("Arial", 'B', 12)
                        title = ReportService._clean_text(name.replace('_', ' ').title())
                        doc.cell(0, 10, txt=title, ln=True)
                        try:
                            # Adjust width so image doesn't overflow
                            doc.image(local_path, x=15, w=170) 
                            doc.ln(5) 
                        except Exception as e:
                            print(f"⚠️ PDF Image Error for {local_path}: {e}")
                            doc.set_font("Arial", 'I', 10)
                            doc.cell(0, 10, txt=f"[Image Error: {e}]", ln=True)
                    else:
                        print(f"⚠️ PDF Generator: Image not found at {local_path}")
                        # Add Placeholder text
                        doc.set_font("Arial", 'B', 12)
                        title = ReportService._clean_text(name.replace('_', ' ').title())
                        doc.cell(0, 10, txt=title, ln=True)
                        doc.set_font("Arial", 'I', 10)
                        doc.set_text_color(255, 0, 0)
                        doc.cell(0, 10, txt="[Image Not Found]", ln=True)
                        doc.set_text_color(0)

            # Save
            os.makedirs("reports", exist_ok=True)
            if output_filename:
                output_path = f"reports/{output_filename}"
            else:
                output_path = f"reports/{session_id}.pdf"
                
            doc.output(output_path)
            print(f"✅ PDF Generated Successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ PDF Generation Error: {e}")
            import traceback
            traceback.print_exc()
            return None

report_service = ReportService()
