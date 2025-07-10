import streamlit as st
import json
import os
import tempfile
from main import parse_resume
from datetime import datetime

def main():
    st.set_page_config(
        page_title="Resume Parser",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 Resume Parser")
    st.markdown("Upload your resume in PDF, DOCX, or TXT format to extract structured information.")
    
    uploaded_file = st.file_uploader(
        "Choose a resume file",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        st.info(f"File size: {uploaded_file.size} bytes")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            with st.spinner("Parsing resume..."):
                result = parse_resume(tmp_file_path)
            
            if result:
                st.success("Resume parsed successfully!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📋 Personal Information")
                    if result.get('name'):
                        st.write(f"**Name:** {result['name']}")
                    if result.get('email'):
                        st.write(f"**Email:** {result['email']}")
                    if result.get('phone'):
                        st.write(f"**Phone:** {result['phone']}")
                    if result.get('linkedin'):
                        st.write(f"**LinkedIn:** {result['linkedin']}")
                    if result.get('address'):
                        st.write(f"**Address:** {result['address']}")
                    
                    if result.get('summary'):
                        st.subheader("📝 Summary")
                        st.write(result['summary'])
                    
                    if result.get('skills'):
                        st.subheader("💼 Skills")
                        skills_html = ""
                        for skill in result['skills']:
                            skills_html += f'<span style="background-color: #000000; color: white; padding: 8px 16px; margin: 4px 6px 4px 0; border-radius: 20px; display: inline-block; font-weight: 500; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">{skill}</span> '
                        st.markdown(skills_html, unsafe_allow_html=True)
                
                with col2:
                    if result.get('work_experience'):
                        st.subheader("💼 Work Experience")
                        for exp in result['work_experience']:
                            with st.expander(f"{exp.get('position', 'N/A')} at {exp.get('company', 'N/A')}"):
                                if exp.get('duration'):
                                    st.write(f"**Duration:** {exp['duration']}")
                                if exp.get('description'):
                                    st.write("**Responsibilities:**")
                                    for desc in exp['description']:
                                        st.write(f"• {desc}")
                    
                    if result.get('education'):
                        st.subheader("🎓 Education")
                        for edu in result['education']:
                            st.write(f"**{edu.get('degree', 'N/A')}**")
                            st.write(f"*{edu.get('university', 'N/A')}*")
                            if edu.get('years'):
                                st.write(f"Years: {edu['years']}")
                            st.write("---")
                
                # Additional sections in full width
                if result.get('certifications'):
                    st.subheader("🏆 Certifications")
                    for cert in result['certifications']:
                        st.write(f"• {cert}")
                
                if result.get('projects'):
                    st.subheader("🚀 Projects")
                    for project in result['projects']:
                        st.write(f"• {project}")
                
                if result.get('languages'):
                    st.subheader("🌐 Languages")
                    lang_cols = st.columns(len(result['languages']))
                    for i, lang in enumerate(result['languages']):
                        with lang_cols[i]:
                            st.write(lang)
                
                if result.get('internships'):
                    st.subheader("🎯 Internships")
                    for internship in result['internships']:
                        st.write(f"• {internship}")
                
                st.subheader("📁 JSON Output")
                with st.expander("View/Download JSON"):
                    st.json(result)
                    
                    json_str = json.dumps(result, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_parsed.json",
                        mime="application/json"
                    )
                
                base_name = os.path.splitext(uploaded_file.name)[0]
                output_path = os.path.join("json_output", f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                os.makedirs("json_output", exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
            else:
                st.error("Failed to parse resume. Please check the file format and content.")
                
        except Exception as e:
            st.error(f"Error parsing resume: {str(e)}")
            st.info("Please ensure the file is not corrupted and contains readable text.")
        
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

if __name__ == "__main__":
    main()