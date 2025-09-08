"""
Streamlit Resume Generator App
Interactive interface for generating Word and PDF resumes from JSON
"""

import streamlit as st
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
import base64
from typing import Dict, Optional
import sys

# Import the resume generator module
from resume_generator import ResumeGenerator, DocumentConfig

# Page configuration
st.set_page_config(
    page_title="Resume Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stDownloadButton>button {
        width: 100%;
        background-color: #008CBA;
        color: white;
        font-weight: bold;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        padding-bottom: 1rem;
        border-bottom: 2px solid #3498db;
    }
    h2 {
        color: #34495e;
        margin-top: 2rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
    }
    </style>
""", unsafe_allow_html=True)


class ResumeApp:
    """Streamlit application for resume generation"""

    def __init__(self):
        self.init_session_state()
        self.setup_sidebar()

    def init_session_state(self):
        """Initialize session state variables"""
        if 'resume_data' not in st.session_state:
            st.session_state.resume_data = self.load_default_data()
        if 'generated_files' not in st.session_state:
            st.session_state.generated_files = {'word': None, 'pdf': None}
        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = False

    def load_default_data(self) -> Dict:
        """Load default resume data from JSON file"""
        default_json_path = "resume_data.json"
        if os.path.exists(default_json_path):
            try:
                with open(default_json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        # Return empty template if no file exists
        return {
            "header": {
                "name": "",
                "phone": "",
                "email": "",
                "location": "",
                "linkedin": "",
                "portfolio": "",
                "github": ""
            },
            "technical_skills": {},
            "education": [],
            "experience": [],
            "projects": [],
            "competitions": [],
            "certifications": []
        }

    def setup_sidebar(self):
        """Setup sidebar configuration"""
        with st.sidebar:
            st.header("⚙️ Configuration")

            # Document settings
            st.subheader("Document Settings")

            # Margins
            col1, col2 = st.columns(2)
            with col1:
                margin_top = st.number_input("Top Margin", 0.1, 2.0, 0.5, 0.1)
                margin_left = st.number_input("Left Margin", 0.1, 2.0, 0.5, 0.1)
            with col2:
                margin_bottom = st.number_input("Bottom Margin", 0.1, 2.0, 0.5, 0.1)
                margin_right = st.number_input("Right Margin", 0.1, 2.0, 0.5, 0.1)

            # Font settings
            st.subheader("Font Settings")
            font_name = st.selectbox("Font Family",
                                     ["Calibri", "Arial", "Times New Roman", "Georgia", "Helvetica"])
            font_size = st.slider("Base Font Size", 9, 14, 11)

            # Store config in session state
            st.session_state.config = DocumentConfig(
                margin_top=margin_top,
                margin_bottom=margin_bottom,
                margin_left=margin_left,
                margin_right=margin_right,
                font_name=font_name,
                font_size_normal=font_size
            )

            st.divider()

            # File operations
            st.subheader("📁 File Operations")

            # Upload JSON
            uploaded_file = st.file_uploader("Upload Resume JSON", type=['json'])
            if uploaded_file:
                try:
                    st.session_state.resume_data = json.loads(uploaded_file.read())
                    st.success("✅ JSON loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Error loading JSON: {str(e)}")

            # Download current JSON
            if st.button("💾 Download Current JSON"):
                json_str = json.dumps(st.session_state.resume_data, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name=f"resume_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

    def edit_header(self):
        """Edit header section"""
        st.subheader("👤 Personal Information")
        header = st.session_state.resume_data.get('header', {})

        col1, col2 = st.columns(2)
        with col1:
            header['name'] = st.text_input("Full Name", header.get('name', ''))
            header['email'] = st.text_input("Email", header.get('email', ''))
            header['phone'] = st.text_input("Phone", header.get('phone', ''))
            header['location'] = st.text_input("Location", header.get('location', ''))

        with col2:
            header['linkedin'] = st.text_input("LinkedIn URL", header.get('linkedin', ''))
            header['portfolio'] = st.text_input("Portfolio URL", header.get('portfolio', ''))
            header['github'] = st.text_input("GitHub URL", header.get('github', ''))

        st.session_state.resume_data['header'] = header

    def edit_technical_skills(self):
        """Edit technical skills section"""
        st.subheader("💻 Technical Skills")

        skills = st.session_state.resume_data.get('technical_skills', {})

        # Add new skill category
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            new_category = st.text_input("Skill Category", key="new_skill_cat")
        with col2:
            new_skills = st.text_input("Skills (comma-separated)", key="new_skills")
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add", key="add_skill"):
                if new_category and new_skills:
                    skills[new_category] = new_skills

        # Display and edit existing skills
        for i, (category, skill_list) in enumerate(list(skills.items())):
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                st.text_input("Category", category, disabled=True, key=f"cat_{i}")
            with col2:
                skills[category] = st.text_input("Skills", skill_list, key=f"skills_{i}")
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_skill_{i}"):
                    del skills[category]
                    st.rerun()

        st.session_state.resume_data['technical_skills'] = skills

    def edit_education(self):
        """Edit education section"""
        st.subheader("🎓 Education")

        education = st.session_state.resume_data.get('education', [])

        # Add new education
        with st.expander("➕ Add New Education"):
            new_edu = {}
            col1, col2 = st.columns(2)
            with col1:
                new_edu['degree'] = st.text_input("Degree", key="new_edu_degree")
                new_edu['school'] = st.text_input("School", key="new_edu_school")
                new_edu['dates'] = st.text_input("Dates", key="new_edu_dates")
            with col2:
                new_edu['location'] = st.text_input("Location", key="new_edu_loc")
                new_edu['gpa'] = st.text_input("GPA (optional)", key="new_edu_gpa")
                notes = st.text_area("Additional Notes (one per line)", key="new_edu_notes")
                new_edu['notes'] = [n.strip() for n in notes.split('\n') if n.strip()]

            if st.button("Add Education"):
                if new_edu['degree'] and new_edu['school']:
                    education.append(new_edu)
                    st.success("✅ Education added!")
                    st.rerun()

        # Display existing education
        for i, edu in enumerate(education):
            with st.expander(f"📚 {edu.get('degree', 'Education')} - {edu.get('school', '')}"):
                col1, col2 = st.columns(2)
                with col1:
                    edu['degree'] = st.text_input("Degree", edu.get('degree', ''), key=f"edu_deg_{i}")
                    edu['school'] = st.text_input("School", edu.get('school', ''), key=f"edu_sch_{i}")
                    edu['dates'] = st.text_input("Dates", edu.get('dates', ''), key=f"edu_dat_{i}")
                with col2:
                    edu['location'] = st.text_input("Location", edu.get('location', ''), key=f"edu_loc_{i}")
                    edu['gpa'] = st.text_input("GPA", edu.get('gpa', ''), key=f"edu_gpa_{i}")

                notes = '\n'.join(edu.get('notes', []))
                notes_input = st.text_area("Additional Notes", notes, key=f"edu_notes_{i}")
                edu['notes'] = [n.strip() for n in notes_input.split('\n') if n.strip()]

                if st.button(f"🗑️ Delete", key=f"del_edu_{i}"):
                    education.pop(i)
                    st.rerun()

        st.session_state.resume_data['education'] = education

    def edit_experience(self):
        """Edit experience section"""
        st.subheader("💼 Experience")

        experience = st.session_state.resume_data.get('experience', [])

        # Add new experience
        with st.expander("➕ Add New Experience"):
            new_exp = {}
            col1, col2 = st.columns(2)
            with col1:
                new_exp['title'] = st.text_input("Job Title", key="new_exp_title")
                new_exp['company'] = st.text_input("Company", key="new_exp_company")
            with col2:
                new_exp['location'] = st.text_input("Location", key="new_exp_loc")
                new_exp['dates'] = st.text_input("Dates", key="new_exp_dates")

            bullets = st.text_area("Bullet Points (one per line)", key="new_exp_bullets")
            new_exp['bullets'] = [b.strip() for b in bullets.split('\n') if b.strip()]

            if st.button("Add Experience"):
                if new_exp['title'] and new_exp['company']:
                    experience.append(new_exp)
                    st.success("✅ Experience added!")
                    st.rerun()

        # Display existing experience
        for i, exp in enumerate(experience):
            with st.expander(f"💼 {exp.get('title', '')} at {exp.get('company', '')}"):
                col1, col2 = st.columns(2)
                with col1:
                    exp['title'] = st.text_input("Title", exp.get('title', ''), key=f"exp_title_{i}")
                    exp['company'] = st.text_input("Company", exp.get('company', ''), key=f"exp_comp_{i}")
                with col2:
                    exp['location'] = st.text_input("Location", exp.get('location', ''), key=f"exp_loc_{i}")
                    exp['dates'] = st.text_input("Dates", exp.get('dates', ''), key=f"exp_dates_{i}")

                bullets = '\n'.join(exp.get('bullets', []))
                bullets_input = st.text_area("Bullet Points", bullets, height=150, key=f"exp_bullets_{i}")
                exp['bullets'] = [b.strip() for b in bullets_input.split('\n') if b.strip()]

                if st.button(f"🗑️ Delete", key=f"del_exp_{i}"):
                    experience.pop(i)
                    st.rerun()

        st.session_state.resume_data['experience'] = experience

    def display_json_editor(self):
        """Display JSON editor for direct editing"""
        st.subheader("📝 Direct JSON Editor")

        json_str = json.dumps(st.session_state.resume_data, indent=2)
        edited_json = st.text_area(
            "Edit JSON directly (be careful with formatting!)",
            json_str,
            height=400
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Apply JSON Changes"):
                try:
                    st.session_state.resume_data = json.loads(edited_json)
                    st.success("✅ JSON updated successfully!")
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON format: {str(e)}")

        with col2:
            if st.button("↩️ Reset to Original"):
                st.session_state.resume_data = self.load_default_data()
                st.success("✅ Reset to original data!")
                st.rerun()

    def generate_resume(self):
        """Generate resume files"""
        st.header("📄 Generate Resume")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🎯 Generate Word & PDF", type="primary"):
                with st.spinner("Generating resume..."):
                    try:
                        # Create temporary directory for output
                        with tempfile.TemporaryDirectory() as temp_dir:
                            # Save current data to temp JSON
                            temp_json = os.path.join(temp_dir, "temp_resume.json")
                            with open(temp_json, 'w', encoding='utf-8') as f:
                                json.dump(st.session_state.resume_data, f, indent=2)

                            # Generate files
                            generator = ResumeGenerator(st.session_state.config)
                            word_path, pdf_path = generator.generate_from_json(
                                temp_json,
                                output_dir=temp_dir,
                                base_name="resume"
                            )

                            # Read generated files
                            with open(word_path, 'rb') as f:
                                word_data = f.read()

                            pdf_data = None
                            if pdf_path and os.path.exists(pdf_path):
                                with open(pdf_path, 'rb') as f:
                                    pdf_data = f.read()

                            # Store in session state
                            st.session_state.generated_files = {
                                'word': word_data,
                                'pdf': pdf_data
                            }

                            st.success("✅ Resume generated successfully!")

                    except Exception as e:
                        st.error(f"❌ Error generating resume: {str(e)}")

        # Display download buttons if files are generated
        if st.session_state.generated_files['word']:
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="📥 Download Word Document",
                    data=st.session_state.generated_files['word'],
                    file_name=f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            with col2:
                if st.session_state.generated_files['pdf']:
                    st.download_button(
                        label="📥 Download PDF",
                        data=st.session_state.generated_files['pdf'],
                        file_name=f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.warning("⚠️ PDF generation failed. Please ensure docx2pdf is installed.")

    def run(self):
        """Run the Streamlit app"""
        st.title("🚀 Resume Generator")
        st.markdown("---")

        # Create tabs for different sections
        tabs = st.tabs([
            "👤 Header",
            "💻 Skills",
            "🎓 Education",
            "💼 Experience",
            "🚀 Projects",
            "🏆 Competitions",
            "📜 Certifications",
            "📝 JSON Editor",
            "📄 Generate"
        ])

        with tabs[0]:
            self.edit_header()

        with tabs[1]:
            self.edit_technical_skills()

        with tabs[2]:
            self.edit_education()

        with tabs[3]:
            self.edit_experience()

        with tabs[4]:
            st.info("Projects section - Similar structure to Experience")
            # You can implement edit_projects() similar to edit_experience()

        with tabs[5]:
            st.info("Competitions section - Similar structure to Education")
            # You can implement edit_competitions()

        with tabs[6]:
            st.info("Certifications section - Simple list with dates")
            # You can implement edit_certifications()

        with tabs[7]:
            self.display_json_editor()

        with tabs[8]:
            self.generate_resume()


# Run the app
if __name__ == "__main__":
    app = ResumeApp()
    app.run()