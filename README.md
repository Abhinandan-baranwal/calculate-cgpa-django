# Calculate CGPA Using Python Django

A beginner-friendly web application for calculating a student's semester grade point average (SGPA) and cumulative grade point average (CGPA). Enter each subject's name, credit value, and grade to see the weighted result.


## Features

- Enter one or more subjects, their credits, and grades.
- Calculate a credit-weighted average (shown as both SGPA and CGPA for the entered set of subjects).
- Add or remove subject rows on the page.
- Get a clear message when an entry is incomplete or invalid.
- Use the page on a desktop or phone.

## Technologies Used

- Python 3.12, 3.13, or 3.14
- Django 6.1
- HTML
- CSS
- A little JavaScript to add subject rows in the browser

## Prerequisites

Install these tools before beginning:

1. **Python 3.12, 3.13, or 3.14.** Check with `python --version` (on some computers, use `python3 --version`).
2. **pip**, Python's package installer. Check with `python -m pip --version`.
3. **Git**, for saving and uploading your project. Check with `git --version`.
4. **A code editor**, such as Visual Studio Code.

During Python installation on Windows, tick the option to add Python to PATH.

## Create and Set Up the Project

### 1. Create a project folder

```bash
mkdir calculate-cgpa
cd calculate-cgpa
```

### 2. (Recommended) Create and activate a virtual environment

A virtual environment keeps this project's Python packages separate from other projects.

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS or Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

When it is active, your terminal usually shows `(.venv)` at the start of the line.

### 3. Install Django

```bash
python -m pip install "Django>=6.1,<6.2"
```

Confirm the installed version:

```bash
python -m django --version
```

### 4. Create the Django project and app

The first command creates the project configuration in the current folder (note the dot at the end). The second creates an app named `calculator`.

```bash
python -m django startproject cgpa_project .
python manage.py startapp calculator
```

### 5. Register the app in `settings.py`

Open `cgpa_project/settings.py`. Find `INSTALLED_APPS` and add `'calculator'` to the list:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'calculator',
]
```

### 6. Create the template and static folders

Inside the `calculator` folder, create these folders:

- `templates/calculator/`
- `static/calculator/`

Also create a new file `calculator/urls.py`. Then add the code from the next section.

## Project Code

### `calculator/views.py`

This view accepts a list of subjects, checks the submitted values, and calculates the weighted average. `Decimal` keeps the arithmetic predictable for display.

```python
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
```

### `calculator/urls.py`

```python
from django.urls import path

from . import views


app_name = "calculator"

urlpatterns = [
    path("", views.index, name="index"),
]
```

### `cgpa_project/urls.py`

Replace the generated project URL file with this version. It connects the home page to the calculator app.

```python
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("calculator.urls")),
]
```

### `calculator/templates/calculator/index.html`

The template includes a CSRF token, which Django requires for a POST form. The **Add subject** button uses JavaScript to add more input rows.

```html
{% load static %}
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CGPA Calculator</title>
    <link rel="stylesheet" href="{% static 'calculator/style.css' %}">
</head>
<body>
    <main class="container">
        <h1>CGPA Calculator</h1>
        <p>Enter each subject's credits and grade. Use the grade scale shown below.</p>
        <p class="scale"><strong>Grade points:</strong> O = 10, A+ = 9, A = 8, B+ = 7, B = 6, C = 5, P = 4, F = 0</p>

        {% if error %}
            <p class="message error" role="alert">{{ error }}</p>
        {% endif %}

        <form method="post">
            {% csrf_token %}
            <div id="subject-rows">
                {% for row in rows %}
                    <div class="subject-row">
                        <label>
                            Subject
                            <input type="text" name="subject[]" value="{{ row.subject }}" placeholder="e.g. Mathematics" required>
                        </label>
                        <label>
                            Credits
                            <input type="number" name="credit[]" value="{{ row.credit }}" min="0.01" step="0.01" placeholder="e.g. 4" required>
                        </label>
                        <label>
                            Grade
                            <select name="grade[]" required>
                                <option value="">Choose a grade</option>
                                {% for grade in grade_options %}
                                    <option value="{{ grade }}" {% if row.grade == grade %}selected{% endif %}>{{ grade }}</option>
                                {% endfor %}
                            </select>
                        </label>
                        <button type="button" class="remove-row" aria-label="Remove this subject">Remove</button>
                    </div>
                {% endfor %}
            </div>

            <div class="actions">
                <button type="button" id="add-row">Add subject</button>
                <button type="submit">Calculate</button>
            </div>
        </form>

        {% if result is not None %}
            <section class="result" aria-live="polite">
                <h2>Your result</h2>
                <p>Weighted average for the entered subjects: <strong>{{ result }}</strong></p>
                <p>For one semester, this is the SGPA. If you enter all subjects across all semesters, it is the overall CGPA.</p>
            </section>
        {% endif %}

        <p class="note">This demo uses an example grading scale. Confirm your institution's grade points before relying on the result.</p>
    </main>

    <script>
        const rowsContainer = document.getElementById("subject-rows");
        const grades = ["O", "A+", "A", "B+", "B", "C", "P", "F"];
        const points = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0};

        document.getElementById("add-row").addEventListener("click", () => {
            const row = document.createElement("div");
            row.className = "subject-row";
            row.innerHTML = `
                <label>Subject
                    <input type="text" name="subject[]" placeholder="e.g. Mathematics" required>
                </label>
                <label>Credits
                    <input type="number" name="credit[]" min="0.01" step="0.01" placeholder="e.g. 4" required>
                </label>
                <label>Grade
                    <select name="grade[]" required>
                        <option value="">Choose a grade</option>
                        ${grades.map(grade => `<option value="${grade}">${grade} (${points[grade]})</option>`).join("")}
                    </select>
                </label>
                <button type="button" class="remove-row" aria-label="Remove this subject">Remove</button>
            `;
            rowsContainer.appendChild(row);
        });

        rowsContainer.addEventListener("click", event => {
            if (event.target.classList.contains("remove-row")) {
                const allRows = rowsContainer.querySelectorAll(".subject-row");
                if (allRows.length > 1) {
                    event.target.closest(".subject-row").remove();
                }
            }
        });
    </script>
</body>
</html>
```

### `calculator/static/calculator/style.css`

```css
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #f3f6fb;
    color: #172033;
    font-family: Arial, sans-serif;
    line-height: 1.5;
}

.container {
    width: min(900px, calc(100% - 32px));
    margin: 40px auto;
    padding: 28px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 8px 28px rgb(20 40 80 / 10%);
}

h1, h2 {
    color: #183b70;
}

.scale, .note {
    padding: 12px;
    background: #eef4ff;
    border-radius: 8px;
}

.subject-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr auto;
    gap: 12px;
    align-items: end;
    margin: 16px 0;
    padding: 16px;
    border: 1px solid #d8e0ed;
    border-radius: 8px;
}

label {
    display: grid;
    gap: 6px;
    font-weight: 600;
}

input, select, button {
    min-height: 40px;
    padding: 8px 10px;
    font: inherit;
}

input, select {
    width: 100%;
    border: 1px solid #aebbd0;
    border-radius: 6px;
}

button {
    border: 0;
    border-radius: 6px;
    background: #245db5;
    color: white;
    cursor: pointer;
}

button:hover {
    background: #17488f;
}

.remove-row {
    background: #68758a;
}

.actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.message, .result {
    margin-top: 20px;
    padding: 16px;
    border-radius: 8px;
}

.error {
    background: #fff0f0;
    color: #9b1c1c;
}

.result {
    background: #eaf8ef;
}

@media (max-width: 650px) {
    .container {
        margin: 16px auto;
        padding: 18px;
    }

    .subject-row {
        grid-template-columns: 1fr;
    }
}
```

## How the CGPA Formula Works

Each grade is converted into a grade point. Multiply each subject's credits by its grade point, add those products, then divide by the sum of all credits:

```text
CGPA = Σ(credit × grade point) / Σ(credits)
```

Here, `Σ` means "add all the values." This is a weighted average: a subject with more credits affects the result more than a subject with fewer credits.

### Worked example

| Subject | Credits | Grade | Grade point | Credits × grade point |
|---|---:|:---:|---:|---:|
| Mathematics | 4 | A | 8 | 32 |
| Physics | 3 | B+ | 7 | 21 |
| English | 2 | O | 10 | 20 |
| **Total** | **9** |  |  | **73** |

```text
CGPA = 73 / 9 = 8.11 (rounded to two decimal places)
```

For a single semester's subjects, this weighted average is usually called **SGPA**. To calculate an overall CGPA, enter the subjects from all completed semesters with their credits and grades. Some institutions have additional rules, so follow your college's official calculation policy.

## Run the Project

From the folder containing `manage.py`, run:

```bash
python manage.py migrate
python manage.py runserver
```

Open this address in your browser:

```text
http://127.0.0.1:8000/
```

Stop the development server by pressing `Ctrl+C` in the terminal.

## Sample Input and Output

**Input:**

| Subject | Credits | Grade |
|---|---:|:---:|
| Mathematics | 4 | A |
| Physics | 3 | B+ |
| English | 2 | O |

**Calculation:** `(4 × 8 + 3 × 7 + 2 × 10) / (4 + 3 + 2) = 73 / 9`

**Output shown on the page:** `Weighted average for the entered subjects: 8.11`

## Project Folder Structure

```text
calculate-cgpa/
├── calculator/
│   ├── migrations/
│   ├── static/
│   │   └── calculator/
│   │       └── style.css
│   ├── templates/
│   │   └── calculator/
│   │       └── index.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── cgpa_project/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

## Upload the Project to GitHub

1. Sign in at [GitHub](https://github.com/) and select **New repository**.
2. Enter a repository name such as `calculate-cgpa-django` and choose **Public**.
3. Leave **Add a README**, **.gitignore**, and **license** unchecked, then select **Create repository**.
4. Copy the repository's HTTPS URL. It looks like `https://github.com/Abhinandan-baranwal/calculate-cgpa-django.git`.
5. In your terminal, go to the folder containing `manage.py`. Create a `.gitignore` file with this content:

```gitignore
   .venv/
   __pycache__/
   *.py[cod]
   db.sqlite3
   .env
```

6. Initialize Git and make the first commit:

```bash
   git init
   git add .
   git commit -m "Add CGPA calculator Django project"
```

7. Set the main branch name, connect your GitHub repository, and push the code. Replace the sample URL with the one you copied:

```bash
   git branch -M main
   git remote add origin https://github.com/your-username/calculate-cgpa-django.git
   git push -u origin main
```

8. Refresh the GitHub repository page to see the uploaded files. GitHub may ask you to sign in from the terminal.

## Future Improvements

- Save student subjects and semester results in a database.
- Add user accounts so each student can save their own results.
- Let users configure their institution's grade scale.
- Add semester-by-semester SGPA and overall CGPA summaries.
- Export a result as a PDF or CSV file.
- Add automated tests and deploy the app online.

## Contributing

This is a learning project. You can fork the repository, make a change on a separate branch, and open a pull request describing what you changed.

## License

No license has been selected for this project. If you publish your own copy, choose a license (for example, MIT) and add it as a `LICENSE` file.

## Author

Abhinandan Baranwal, SRMIST
