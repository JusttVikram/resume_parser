import os
import re
import json
import docx
import pdfplumber
from typing import List, Dict
from ocr import ocr_from_image
from pdf2image import convert_from_path

def load_text_from_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        text_pages = []
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            if not page_text.strip():
                try:
                    images = convert_from_path(file_path, first_page=i+1, last_page=i+1)
                    if images:
                        page_text = ocr_from_image(images[0])
                except Exception:
                    pass
            text_pages.append(page_text)
        return "\n".join(text_pages)

def load_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)

def load_text_from_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def load_resume(file_path: str) -> str:
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        return load_text_from_pdf(file_path)
    elif ext == ".docx":
        return load_text_from_docx(file_path)
    elif ext == ".txt":
        return load_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

def extract_section(text: str, header: str, stop_headers: List[str] = None) -> str:
    stop_headers = stop_headers or [
        "Skills", "Work Experience", "Experience", "Education",
        "Certifications", "Projects", "Languages", "Internships", "Summary"
    ]
    stop_pattern = "|".join([rf"\n{re.escape(h)}[:\n]" for h in stop_headers if h.lower() != header.lower()])
    pattern = rf"{re.escape(header)}[:\n](.*?)(?={stop_pattern}|\Z)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_name(text: str) -> str:
    lines = text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if any(term in line.lower() for term in ["email", "phone", "linkedin", "skills", "experience", "education", "summary", "objective", "address", "contact"]):
            continue
        if re.match(r"^[A-Z][a-z]+( [A-Z][a-z]+)+$", line):
            return line
    return ""

def extract_education(text: str) -> List[Dict]:
    edu_block = extract_section(text, "Education")
    education = []
    for line in edu_block.split("\n"):
        line = line.strip()
        if not line:
            continue
        match = re.search(r"(.+?),\s*(.+?),\s*(\d{4})(?:\s*[-–—]\s*(\d{4}|Present))?", line)
        if match:
            degree = match.group(1).strip()
            university = match.group(2).strip()
            years = match.group(3).strip()
            if match.group(4):
                years += f"-{match.group(4).strip()}"
            education.append({
                "degree": degree,
                "university": university,
                "years": years
            })
        else:
            parts = [p.strip() for p in line.split(",") if p.strip()]
            if len(parts) >= 2:
                education.append({
                    "degree": parts[0],
                    "university": parts[1],
                    "years": parts[2] if len(parts) > 2 else ""
                })
    return education

def extract_work_experience(text: str) -> List[Dict]:
    exp_block = extract_section(text, "Work Experience") or extract_section(text, "Experience")
    experience = []
    if not exp_block:
        return experience
    
    blocks = re.split(r"\n\s*\n", exp_block)
    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if not lines:
            continue
        
        exp = {}
        description_lines = []
        
        for line in lines:
            if re.search(r"^(Company|Employer|Organization):\s*", line, re.I):
                exp["company"] = re.sub(r"^(Company|Employer|Organization):\s*", "", line, flags=re.I).strip()
            elif re.search(r"^(Position|Title|Role|Job Title):\s*", line, re.I):
                exp["position"] = re.sub(r"^(Position|Title|Role|Job Title):\s*", "", line, flags=re.I).strip()
            elif re.search(r"^(Duration|Dates|Period|Timeline):\s*", line, re.I):
                exp["duration"] = re.sub(r"^(Duration|Dates|Period|Timeline):\s*", "", line, flags=re.I).strip()
            elif line.startswith("-") or line.startswith("•"):
                description_lines.append(line.lstrip("-• ").strip())
        
        if not exp.get("company") or not exp.get("position"):
            first_line = lines[0] if lines else ""
            if " at " in first_line:
                parts = first_line.split(" at ", 1)
                exp["position"] = exp.get("position") or parts[0].strip()
                company_part = parts[1].strip()
                if " - " in company_part or " – " in company_part or " — " in company_part:
                    company_parts = re.split(r'\s*[-–—]\s*', company_part, 1)
                    exp["company"] = exp.get("company") or company_parts[0].strip()
                    if len(company_parts) > 1:
                        exp["duration"] = exp.get("duration") or company_parts[1].strip()
                elif "(" in company_part and ")" in company_part:
                    match = re.match(r'(.+?)\s*\(([^)]+)\)', company_part)
                    if match:
                        exp["company"] = exp.get("company") or match.group(1).strip()
                        exp["duration"] = exp.get("duration") or match.group(2).strip()
                else:
                    exp["company"] = exp.get("company") or company_part
            elif " | " in first_line or " - " in first_line or " – " in first_line:
                separators = [" | ", " - ", " – ", " — "]
                for sep in separators:
                    if sep in first_line:
                        parts = first_line.split(sep)
                        if len(parts) >= 2:
                            exp["position"] = exp.get("position") or parts[0].strip()
                            exp["company"] = exp.get("company") or parts[1].strip()
                            if len(parts) >= 3:
                                exp["duration"] = exp.get("duration") or parts[2].strip()
                        break
        
        used = {exp.get("company", ""), exp.get("position", ""), exp.get("duration", "")}
        for line in lines[1:]:
            if (line not in used and not re.search(r'^(Company|Employer|Organization|Position|Title|Role|Job Title|Duration|Dates|Period|Timeline):', line, re.I)):
                if line.startswith("-") or line.startswith("•"):
                    description_lines.append(line.lstrip("-• ").strip())
                elif len(line) > 2:
                    description_lines.append(line.strip())
        
        clean_description = [desc for desc in description_lines if desc and len(desc) > 2]
        if clean_description:
            exp["description"] = clean_description
        
        if exp.get("position") or exp.get("company"):
            experience.append(exp)
    return experience

def extract_summary(text: str) -> str:
    summary = extract_section(text, "Summary")
    if not summary:
        summary = extract_section(text, "Objective")
    return summary

def extract_email(text: str) -> str:
    match = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', text)
    return match.group(0) if match else None

def extract_phone(text: str) -> str:
    patterns = [
        r'(\+?1[-.\s]?)?\(([0-9]{3})\)[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
        r'(\+?1[-.\s]?)?([0-9]{3})[-.\s]([0-9]{3})[-.\s]([0-9]{4})',
        r'(\+?1[-.\s]?)?([0-9]{3})\.([0-9]{3})\.([0-9]{4})',
        r'(\+?1[-.\s]?)?([0-9]{3})\s([0-9]{3})\s([0-9]{4})',
        r'(\+?1[-.\s]?)?([0-9]{10})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return None

def extract_linkedin(text: str) -> str:
    match = re.search(r'(https?://)?(www\.)?linkedin\.com/[^\s]+', text)
    if match:
        url = match.group(0)
        url = re.sub(r'^(https?://)?(www\.)?', '', url)
        return url.strip()
    return None

def extract_skills(text: str) -> List[str]:
    raw = extract_section(text, "Skills")
    items = [i.strip() for i in re.split(r"[•,\n]", raw) if i.strip()]
    blacklist = {"street", "road", "city", "state", "india", "usa"}
    skills = [i for i in items if not any(b in i.lower() for b in blacklist)]
    return list(dict.fromkeys([s for s in skills if s]))

def extract_address(text: str) -> str:
    lines = text.split("\n")[:10]
    address_parts = []
    for line in lines:
        if any(x in line.lower() for x in ["street", "ave", "road", "zip", "city", "state", "district"]):
            address_parts.append(line.strip())
    return ", ".join(address_parts) if address_parts else None

def extract_certifications(text: str) -> List[str]:
    raw = extract_section(text, "Certifications")
    return [c.strip("–• ") for c in raw.split("\n") if c.strip()]

def extract_languages(text: str) -> List[str]:
    raw = extract_section(text, "Languages")
    return [l.strip() for l in re.split(r",|\n|•", raw) if l.strip()]

def extract_projects(text: str) -> List[str]:
    raw = extract_section(text, "Projects")
    return [p.strip("–• ") for p in raw.split("\n") if p.strip()]

def detect_internships(text: str) -> List[str]:
    return list(set(re.findall(r"(Intern(?:ship)? at .+|.+ Intern\b)", text, re.IGNORECASE)))

def parse_resume(file_path: str) -> Dict:
    text = load_resume(file_path)
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    linkedin = extract_linkedin(text)
    skills = extract_skills(text)
    work_experience = extract_work_experience(text)
    education = extract_education(text)
    certifications = extract_certifications(text)
    languages = extract_languages(text)
    projects = extract_projects(text)
    internships = detect_internships(text)
    address = extract_address(text)
    summary = extract_summary(text)
    
    result = {}
    if name: result["name"] = name
    if email: result["email"] = email
    if phone: result["phone"] = phone
    if linkedin: result["linkedin"] = linkedin
    if summary: result["summary"] = summary
    if address: result["address"] = address
    if skills: result["skills"] = skills
    if work_experience: result["work_experience"] = work_experience
    if education: result["education"] = education
    if certifications: result["certifications"] = certifications
    if languages: result["languages"] = languages
    if projects: result["projects"] = projects
    if internships: result["internships"] = internships
    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("resume_path")
    args = parser.parse_args()
    result = parse_resume(args.resume_path)
    print(json.dumps(result, indent=2))
    # Save output to json_output/
    base = os.path.basename(args.resume_path)
    name, _ = os.path.splitext(base)
    output_path = os.path.join("json_output", f"{name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nJSON output saved to {output_path}")