import re


def extract_invoice_details(text):
    """
    Extract important information from invoice text.
    """

    details = {}

    invoice_number = re.search(
        r"Invoice Number:\s*(.+)",
        text,
        re.IGNORECASE
    )

    date = re.search(
        r"Date:\s*(.+)",
        text,
        re.IGNORECASE
    )

    customer = re.search(
        r"Customer:\s*(.+)",
        text,
        re.IGNORECASE
    )

    amount = re.search(
        r"Total:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if invoice_number:
        details["invoice_number"] = invoice_number.group(1).strip()

    if date:
        details["date"] = date.group(1).strip()

    if customer:
        details["customer"] = customer.group(1).strip()

    if amount:
        details["total_amount"] = amount.group(1).strip()

    return details

def extract_resume_details(text):
    """
    Extract important information from resume text.
    """

    details = {}

    name = re.search(
        r"Name:\s*(.+)",
        text,
        re.IGNORECASE
    )

    email = re.search(
        r"Email:\s*(.+)",
        text,
        re.IGNORECASE
    )

    education = re.search(
        r"Education:\s*(.+)",
        text,
        re.IGNORECASE
    )

    experience = re.search(
        r"Experience:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if name:
        details["name"] = name.group(1).strip()

    if email:
        details["email"] = email.group(1).strip()

    if education:
        details["education"] = education.group(1).strip()

    if experience:
        details["experience"] = experience.group(1).strip()

    return details

def extract_marksheet_details(text):
    """
    Extract important information from marksheet text.
    Supports simple and real-world marksheet formats.
    """

    details = {}
    lines = [line.strip() for line in text.splitlines()]

    # -------------------------------------------------
    # Student Name - Simple format
    # -------------------------------------------------

    student_name = re.search(
        r"Student Name:\s*(.+)",
        text,
        re.IGNORECASE
    )

    # -------------------------------------------------
    # Student Name - Real marksheet
    # -------------------------------------------------

    if not student_name:

        for i, line in enumerate(lines):

            if "FULL NAM" in line.upper():

                # The candidate's name is normally
                # on the next non-empty line.
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
    # Roll Number - Simple format
    # -------------------------------------------------

    roll_number = re.search(
        r"Roll Number:\s*(.+)",
        text,
        re.IGNORECASE
    )

    # -------------------------------------------------
    # Seat Number - Real marksheet
    # -------------------------------------------------

    if not roll_number:

        for i, line in enumerate(lines):

            if "SEATNO" in line.upper():

                # In this OCR layout the seat number
                # appears a few lines below the heading.
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
    # Total - Simple format
    # -------------------------------------------------

    total = re.search(
        r"Total:\s*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    # -------------------------------------------------
    # Total - Real marksheet
    # -------------------------------------------------

    if not total:

        for i, line in enumerate(lines):

            if line.lower() == "total marks":

                # Search backwards/forwards around
                # "Total Marks" for numeric values.
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

                # The last numeric value before
                # "Total Marks" is the obtained total.
                if numeric_values:
                    total = re.match(
                        r"(\d+)",
                        numeric_values[-1]
                    )

                break

    # -------------------------------------------------
    # Percentage - Simple format
    # -------------------------------------------------

    percentage = re.search(
        r"Percentage\s*:?\s*(\d+(?:\.\d+)?)\s*%?",
        text,
        re.IGNORECASE
    )

    # -------------------------------------------------
    # Percentage - Real marksheet
    # -------------------------------------------------

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

def extract_resume_skills(text):
    """
    Extract skills listed in a resume.
    """

    skills = []

    lines = text.splitlines()
    collecting = False

    for line in lines:
        line = line.strip()

        if line.lower() == "skills:":
            collecting = True
            continue

        if collecting:
            if line.endswith(":"):
                break

            if line:
                skills.append(line)

    return skills

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