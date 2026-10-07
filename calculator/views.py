from decimal import Decimal, InvalidOperation

from django.shortcuts import render


# Example scale only: replace these values if your college uses another scale.
GRADE_POINTS = {
    "O": Decimal("10"),
    "A+": Decimal("9"),
    "A": Decimal("8"),
    "B+": Decimal("7"),
    "B": Decimal("6"),
    "C": Decimal("5"),
    "P": Decimal("4"),
    "F": Decimal("0"),
}


def index(request):
    rows = [{"subject": "", "credit": "", "grade": ""}]
    result = None
    error = None

    if request.method == "POST":
        subjects = request.POST.getlist("subject[]")
        credits = request.POST.getlist("credit[]")
        grades = request.POST.getlist("grade[]")
        rows = []
        weighted_points = Decimal("0")
        total_credits = Decimal("0")

        if not (len(subjects) == len(credits) == len(grades)):
            error = "The form data did not match. Please refresh the page and try again."
        else:
            for subject, credit_text, grade_text in zip(subjects, credits, grades):
                subject = subject.strip()
                credit_text = credit_text.strip()
                grade = grade_text.strip().upper()

                # Ignore a completely unused row, for example an extra blank row.
                if not subject and not credit_text and not grade:
                    continue

                rows.append(
                    {"subject": subject, "credit": credit_text, "grade": grade}
                )

                if not subject or not credit_text or not grade:
                    error = "Fill in the subject, credits, and grade for every used row."
                    break

                try:
                    credit = Decimal(credit_text)
                except InvalidOperation:
                    error = f"Credits for {subject} must be a number."
                    break

                if not credit.is_finite() or credit <= 0:
                    error = f"Credits for {subject} must be greater than zero."
                    break

                if grade not in GRADE_POINTS:
                    allowed = ", ".join(GRADE_POINTS)
                    error = f"Grade for {subject} is not recognized. Use: {allowed}."
                    break

                weighted_points += credit * GRADE_POINTS[grade]
                total_credits += credit

            if not error and total_credits == 0:
                error = "Enter at least one complete subject before calculating."

            if not error:
                result = (weighted_points / total_credits).quantize(Decimal("0.01"))

    return render(
        request,
        "calculator/index.html",
        {
            "rows": rows,
            "result": result,
            "error": error,
            "grade_options": GRADE_POINTS.keys(),
        },
    )