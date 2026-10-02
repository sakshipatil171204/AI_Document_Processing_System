def validate_invoice(details):
    """
    Validate extracted invoice information.
    """

    required_fields = [
        "total_amount"
    ]

    missing_fields = []

    for field in required_fields:
        if not details.get(field):
            missing_fields.append(field)

    if missing_fields:
        return {
            "valid": False,
            "message": "Missing fields: " + ", ".join(missing_fields)
        }

    return {
        "valid": True,
        "message": "Invoice information is valid."
    }


def validate_resume(details):
    """
    Validate extracted resume information.
    """

    required_fields = [
        "name",
        "email"
    ]

    missing_fields = []

    for field in required_fields:
        if not details.get(field):
            missing_fields.append(field)

    if missing_fields:
        return {
            "valid": False,
            "message": "Missing fields: " + ", ".join(missing_fields)
        }

    return {
        "valid": True,
        "message": "Resume information is valid."
    }


def validate_marksheet(details):
    """
    Validate extracted marksheet information.

    Supports:
    1. Marksheets with total and percentage.
    2. University Statements of Grade with credits, EGP and SGPA.
    """

    # University Statement of Grade
    if details.get("sgpa") or details.get("egp") or details.get("credits"):

        required_fields = [
            "student_name",
            "result"
        ]

    # Regular marksheet
    else:

        required_fields = [
            "student_name",
            "total",
            "percentage"
        ]

    missing_fields = []

    for field in required_fields:
        if not details.get(field):
            missing_fields.append(field)

    if missing_fields:
        return {
            "valid": False,
            "message": "Missing fields: " + ", ".join(missing_fields)
        }

    return {
        "valid": True,
        "message": "Marksheet information is valid."
    }