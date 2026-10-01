import re


def extract_invoice_details(text):
    """
    Extract important information from invoice text.
    Supports simple and realistic invoice formats.
    """

    details = {}
    lines = [line.strip() for line in text.splitlines()]

    # Invoice Number
    invoice_number = re.search(
        r"Invoice\s*(?:Number|No\.?)\s*:?\s*(.+)",
        text,
        re.IGNORECASE
    )

    if invoice_number:
        details["invoice_number"] = invoice_number.group(1).strip()

    # Date
    date_match = re.search(
        r"Date(?:\s+of\s+issue)?\s*:?\s*(.+)",
        text,
        re.IGNORECASE
    )

    if date_match:
        details["date"] = date_match.group(1).strip()

    # Customer / Client - simple invoice format
    customer_match = re.search(
        r"Customer\s*:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if customer_match:
        details["client"] = customer_match.group(1).strip()

    # Seller and Client - realistic invoice format
    if "Seller:" in text and "Client:" in text:

        seller_index = lines.index("Seller:") if "Seller:" in lines else -1
        client_index = lines.index("Client:") if "Client:" in lines else -1

        if seller_index != -1 and client_index != -1:

            # In this OCR format, the names appear after Seller/Client labels.
            name_lines = []

            for line in lines[client_index + 1:]:
                if line and line not in ["ITEMS"]:
                    name_lines.append(line)

                if len(name_lines) == 2:
                    break

            if len(name_lines) >= 2:
                details["seller"] = name_lines[0]
                details["client"] = name_lines[1]

    # Item
    item_match = re.search(
        r"Item\s*:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if item_match:
        details["item"] = item_match.group(1).strip()

    # Quantity
    quantity_match = re.search(
        r"Quantity\s*:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if quantity_match:
        details["quantity"] = quantity_match.group(1).strip()

    # Amount for simple invoice
    amount_match = re.search(
        r"Amount\s*:\s*([\d,.\s]+)",
        text,
        re.IGNORECASE
    )

    if amount_match:
        amount = amount_match.group(1).replace(",", "").replace(" ", "")
        details["amount"] = amount

    # Total
    total_match = re.search(
        r"Total\s*:\s*([\d,.\s]+)",
        text,
        re.IGNORECASE
    )

    if total_match:

        total = total_match.group(1)
        total = total.replace(",", ".").replace(" ", "")

        details["total_amount"] = total

    else:
        # Realistic invoice:
        # Total
        # $22,68
        # $2,27
        # $24,95

        for i, line in enumerate(lines):

            if line.lower() == "total":

                amounts = []

                for next_line in lines[i + 1:i + 5]:

                    cleaned = next_line.replace("$", "").strip()

                    match = re.fullmatch(
                        r"\d+(?:[.,]\d{2})",
                        cleaned
                    )

                    if match:
                        amount = cleaned.replace(",", ".")
                        amounts.append(amount)

                if amounts:
                    # Last amount is the gross total
                    details["total_amount"] = amounts[-1]

                break

    return details

def extract_resume_details(text):
    """
    Extract important information from resume text.
    """

    details = {}
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Name
    name_match = re.search(
        r"Name\s*:\s*([A-Za-z][A-Za-z .'-]+)",
        text,
        re.IGNORECASE
    )

    if name_match:
        details["name"] = name_match.group(1).strip()
    else:
        # Usually the first line of a resume is the person's name.
        first_line = lines[0] if lines else ""

        if (
            re.fullmatch(
                r"[A-Za-z]+(?:\s+[A-Za-z]+){1,3}",
                first_line
            )
            and first_line.upper() not in [
                "RESUME",
                "CURRICULUM VITAE"
            ]
        ):
            details["name"] = first_line

    # Email
    email_match = re.search(
        r"[\w\.-]+@[\w\.-]+\.\w+",
        text
    )

    if email_match:
        details["email"] = email_match.group(0)

    # Phone
    # Require a realistic phone-number pattern so that
    # years such as 1998-2003 are not detected as phone numbers.
    phone_match = re.search(
        r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)",
        text
    )

    if phone_match:
        phone = phone_match.group(0).strip()

        # Reject date/year ranges such as 1998-2003
        if not re.fullmatch(
            r"\d{4}\s*[-–]\s*\d{4}",
            phone
        ):
            details["phone"] = phone

    # Education
    education_match = re.search(
        r"Education\s*:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if education_match:
        details["education"] = education_match.group(1).strip()
    else:
        for i, line in enumerate(lines):
            if line.upper() == "EDUCATION":
                education_lines = []

                for next_line in lines[i + 1:i + 5]:
                    if next_line.upper() in [
                        "EXPERIENCE",
                        "SKILLS",
                        "LANGUAGES",
                        "REFERENCES"
                    ]:
                        break

                    education_lines.append(next_line)

                if education_lines:
                    details["education"] = " ".join(education_lines)

                break

    return details
def extract_resume_skills(text):
    """
    Extract skills from a resume.
    Supports normal Skills sections and
    skill/training information embedded in text.
    """

    skills = []

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Common skills that may appear in resumes.
    known_skills = [
        "Python",
        "Java",
        "SQL",
        "HTML",
        "CSS",
        "JavaScript",
        "C++",
        "C",
        "PHP",
        "MySQL",
        "MongoDB",
        "Excel",
        "Power BI",
        "Machine Learning",
        "Data Science",
        "Data Analysis",
        "Data Mining",
        "Leadership",
        "Communication",
        "Problem Solving",
        "Teamwork",
        "Collaboration",
        "Personal Training",
        "NASM CPT",
        "Nutrition Coaching",
        "ISSA Fitness Nutrition",
        "Alpha Coach",
        "TEAM Fitness Instructor"
    ]

    text_lower = text.lower()

    # 1. Extract skills from a normal SKILLS section
    collecting = False

    for line in lines:

        upper_line = line.upper()

        if upper_line in ["SKILLS", "TECHNICAL SKILLS"]:
            collecting = True
            continue

        if collecting:

            if upper_line in [
                "EXPERIENCE",
                "PROFESSIONAL EXPERIENCE",
                "EDUCATION",
                "LANGUAGES",
                "CERTIFICATIONS",
                "AWARDS"
            ]:
                break

            # Split common separators
            parts = re.split(r"[,|/•\-]+", line)

            for part in parts:
                skill = part.strip()

                if skill and len(skill) > 1:
                    skills.append(skill)

    # 2. Detect known skills anywhere in the resume.
    # This handles resumes without a dedicated Skills section.
    for skill in known_skills:

        if skill.lower() in text_lower:
            skills.append(skill)

    # Remove duplicates while preserving order
    unique_skills = []

    for skill in skills:
        if skill not in unique_skills:
            unique_skills.append(skill)

    return unique_skills

def extract_marksheet_details(text):
    """
    Extract important information from marksheet text.
    Supports simple and real-world marksheet formats.
    """

    details = {}

    lines = [line.strip() for line in text.splitlines()]

    # -------------------------------------------------
    # Student Name
    # -------------------------------------------------

    student_name = re.search(
        r"Student Name:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if not student_name:
        for i, line in enumerate(lines):
            if "FULL NAM" in line.upper():
                for next_line in lines[i + 1:i + 4]:
                    if re.fullmatch(
                        r"[A-Za-z][A-Za-z .'-]+",
                        next_line
                    ):
                        student_name = re.match(
                            r"(.+)",
                            next_line
                        )
                        break

    # -------------------------------------------------
    # Roll Number
    # -------------------------------------------------

    roll_number = re.search(
        r"Roll Number:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if not roll_number:
        for i, line in enumerate(lines):
            if "SEATNO" in line.upper():
                for next_line in lines[i + 1:i + 6]:
                    if re.fullmatch(
                        r"[A-Z]\d{5,10}",
                        next_line
                    ):
                        roll_number = re.match(
                            r"(.+)",
                            next_line
                        )
                        break

    # -------------------------------------------------
    # Total Marks
    # -------------------------------------------------

    total = re.search(
        r"Total:\s*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    if not total:
        for i, line in enumerate(lines):
            if line.lower() == "total marks":
                numeric_values = []

                for nearby_line in lines[i - 6:i + 3]:
                    match = re.fullmatch(
                        r"\d{1,4}",
                        nearby_line
                    )

                    if match:
                        numeric_values.append(
                            match.group(0)
                        )

                if numeric_values:
                    total = re.match(
                        r"(\d+)",
                        numeric_values[-1]
                    )

                break

    # -------------------------------------------------
    # Percentage
    # -------------------------------------------------

    percentage = re.search(
        r"Percentage\s*:?\s*(\d+(?:\.\d+)?)\s*%?",
        text,
        re.IGNORECASE
    )

    if not percentage:
        for i, line in enumerate(lines):
            if "PERCENTAGE" in line.upper():
                for next_line in lines[i + 1:i + 5]:
                    match = re.fullmatch(
                        r"\d+(?:\.\d+)",
                        next_line
                    )

                    if match:
                        percentage = re.match(
                            r"(.+)",
                            next_line
                        )
                        break

    # -------------------------------------------------
    # Store extracted information
    # -------------------------------------------------

    if student_name:
        details["student_name"] = student_name.group(1).strip()

    if roll_number:
        details["roll_number"] = roll_number.group(1).strip()

    if total:
        details["total"] = total.group(1).strip()

    if percentage:
        details["percentage"] = percentage.group(1).strip() + "%"

    # -------------------------------------------------
    # Result
    # -------------------------------------------------

    result = re.search(
        r"\b(PASS|FAIL)\b",
        text,
        re.IGNORECASE
    )

    if result:
        details["result"] = result.group(1).upper()

    return details
def extract_subject_marks(text):
    """
    Extract subject names and obtained marks
    from simple and real-world marksheet formats.
    """

    subject_marks = {}

    lines = text.splitlines()

    # Subjects that are commonly non-numeric grade subjects.
    grade_subject_patterns = [
        "HEALTH & PHYSICAL EDUCATION",
        "DEFENCE STUDIES",
        "SELF DEVELOPMENT & ART APPRE",
        "ENV. EDU. & WATER SECURITY"
    ]

    i = 0

    while i < len(lines):

        line = lines[i].strip()

        # -------------------------------------------------
        # Format 1: Simple format
        # Example:
        # Python: 82
        # DBMS: 78
        # -------------------------------------------------

        simple_match = re.match(
            r"^(.+):\s*(\d+(?:\.\d+)?)$",
            line
        )

        if simple_match:
            subject = simple_match.group(1).strip()
            marks = simple_match.group(2).strip()

            if subject.lower() not in [
                "total",
                "percentage"
            ]:
                subject_marks[subject] = marks

            i += 1
            continue

        # -------------------------------------------------
        # Format 2: Real marksheet
        # Example:
        # 01 MARATHI (1ST LANG)
        # 100
        # 089
        # EIGHTYNINE
        # -------------------------------------------------

        subject_match = re.match(
            r"^\d{1,3}\s+(.+)$",
            line
        )

        if subject_match:

            subject = subject_match.group(1).strip()

            # Ignore non-subject headings
            ignored_words = [
                "CANDIDATE",
                "SUBJECT CODE",
                "TOTAL",
                "SEAT NO",
                "CENTRE NO",
                "DIST.",
                "MONTH",
                "STREAM"
            ]

            if not any(
                word in subject.upper()
                for word in ignored_words
            ):

                # Look at the next few lines for numeric marks.
                nearby_lines = lines[i + 1:i + 5]

                numeric_values = []

                for next_line in nearby_lines:

                    next_line = next_line.strip()

                    # Only accept standalone numbers.
                    number_match = re.fullmatch(
                        r"\d{1,3}",
                        next_line
                    )

                    if number_match:
                        numeric_values.append(
                            number_match.group(0)
                        )

                # Usually:
                # first number = maximum marks
                # second number = obtained marks
                if len(numeric_values) >= 2:

                    obtained_marks = numeric_values[1]

                    subject_marks[subject] = obtained_marks

        i += 1

    return subject_marks