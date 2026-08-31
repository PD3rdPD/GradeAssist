"""Student Grade Calculator with an enhanced graphical interface."""

from __future__ import annotations

import csv
import json
import math
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


PREFERENCES_FILE = Path("grade_calculator_preferences.json")

APP_NAME = "GradeAssist"
APP_VERSION = "0.9 Beta"
APP_BUILD_LABEL = "Teacher Feedback Build"


LANGUAGES = {
    "English": {
        "title": "Student Grade Calculator",
        "subtitle": "Plan. Calculate. Improve.",
        "student_name": "Student Name:",
        "grades": "Grades:",
        "instructions": (
            "Enter grades separated by commas.\n"
            "Example: 85, 92, 78, 100"
        ),
        "allow_extra_credit": "Allow grades over 100",
        "extra_credit_points": "Standalone Extra Credit Points:",
        "calculate": "Calculate Grade",
        "average": "Average",
        "letter_grade": "Letter Grade",
        "progress": "Progress",
        "desired_grade": "Desired Final Grade:",
        "remaining": "Remaining Assignments:",
        "goal": "Calculate Grade Goal",
        "path": "Grade Path Planning",
        "export": "Export to CSV",
        "clear": "Clear / Reset",
        "dark": "Dark Mode",
        "light": "Light Mode",
        "large_text": "Larger Text",
        "language": "Language:",
        "missing_name": "Please enter the student's name.",
        "invalid_grades": "Invalid Grades",
        "calculate_first": "Please calculate the current grade first.",
        "export_complete": "Export Complete",
        "no_results": "Calculate a grade before exporting.",
    },
    "Español": {
        "title": "Calculadora de Calificaciones",
        "subtitle": "Planifica. Calcula. Mejora.",
        "student_name": "Nombre del Estudiante:",
        "grades": "Calificaciones:",
        "instructions": (
            "Ingrese las calificaciones separadas por comas.\n"
            "Ejemplo: 85, 92, 78, 100"
        ),
        "allow_extra_credit": "Permitir calificaciones mayores de 100",
        "extra_credit_points": "Puntos de Crédito Extra:",
        "calculate": "Calcular Calificación",
        "average": "Promedio",
        "letter_grade": "Letra",
        "progress": "Progreso",
        "desired_grade": "Calificación Final Deseada:",
        "remaining": "Tareas Restantes:",
        "goal": "Calcular Meta",
        "path": "Plan de Calificaciones",
        "export": "Exportar a CSV",
        "clear": "Borrar / Reiniciar",
        "dark": "Modo Oscuro",
        "light": "Modo Claro",
        "large_text": "Texto Grande",
        "language": "Idioma:",
        "missing_name": "Ingrese el nombre del estudiante.",
        "invalid_grades": "Calificaciones Inválidas",
        "calculate_first": "Primero calcule la calificación actual.",
        "export_complete": "Exportación Completa",
        "no_results": "Calcule una calificación antes de exportar.",
    },
}


def calculate_average(
    grades: list[float],
    extra_credit_points: float = 0,
) -> float:
    """Calculate the average with optional extra-credit points."""

    if not grades:
        raise ValueError("At least one grade is required.")

    return (sum(grades) + extra_credit_points) / len(grades)


def letter_grade(average: float) -> str:
    """Convert a numerical average into a letter grade."""

    if average >= 90:
        return "A"
    if average >= 80:
        return "B"
    if average >= 70:
        return "C"
    if average >= 60:
        return "D"

    return "F"


def parse_grades(
    raw_grades: str,
    allow_over_100: bool = False,
) -> list[float]:
    """Parse and validate comma-separated grades."""

    if not raw_grades.strip():
        raise ValueError("Please enter at least one grade.")

    grades: list[float] = []

    for item in raw_grades.split(","):
        item = item.strip()

        if not item:
            raise ValueError("Grades cannot contain blank entries.")

        try:
            grade = float(item)
        except ValueError as exc:
            raise ValueError(
                f"'{item}' is not a valid number."
            ) from exc

        if grade < 0:
            raise ValueError("Grades cannot be negative.")

        if grade > 100 and not allow_over_100:
            raise ValueError(
                "Grades over 100 require the "
                "'Allow grades over 100' option."
            )

        grades.append(grade)

    return grades


def calculate_required_grade(
    grades: list[float],
    target_average: float,
    remaining_assignments: int,
    extra_credit_points: float = 0,
) -> float:
    """Calculate the average needed on remaining assignments."""

    if not grades:
        raise ValueError("At least one current grade is required.")

    if not 0 <= target_average <= 100:
        raise ValueError(
            "Target grade must be between 0 and 100."
        )

    if remaining_assignments <= 0:
        raise ValueError(
            "Remaining assignments must be greater than zero."
        )

    current_total = sum(grades) + extra_credit_points

    final_count = (
        len(grades) + remaining_assignments
    )

    target_total = (
        target_average * final_count
    )

    points_needed = (
        target_total - current_total
    )

    return points_needed / remaining_assignments


def progress_feedback(
    average: float,
    target: float | None = None,
) -> str:
    """Generate simple grade-progress feedback."""

    if average >= 90:
        message = (
            "Excellent work! You are currently performing "
            "at an A level."
        )

    elif average >= 80:
        message = (
            "You are doing well. A few stronger grades "
            "could move you toward an A."
        )

    elif average >= 70:
        message = (
            "You are passing, but stronger upcoming grades "
            "could significantly improve your average."
        )

    elif average >= 60:
        message = (
            "Your grade is currently at risk. Focus on upcoming "
            "assignments and available extra credit."
        )

    else:
        message = (
            "Your current average is below passing. Focus on "
            "upcoming assignments and any recovery opportunities."
        )

    if target is not None:

        difference = target - average

        if difference > 0:
            message += (
                f"\nYou are {difference:.2f} percentage points "
                f"below your {target:.2f}% target."
            )

        elif difference < 0:
            message += (
                f"\nYou are {abs(difference):.2f} percentage "
                "points above your target."
            )

        else:
            message += (
                "\nYou are exactly at your target."
            )

    return message


def build_even_path(
    needed_average: float,
    remaining: int,
) -> tuple[int, ...]:
    """Create a consistent-score path."""

    score = max(
        0,
        math.ceil(needed_average),
    )

    return tuple(
        score
        for _ in range(remaining)
    )


def build_rising_path(
    needed_average: float,
    remaining: int,
) -> tuple[int, ...]:
    """Create a path that starts lower and finishes stronger."""

    if remaining == 1:
        return (
            max(
                0,
                math.ceil(needed_average),
            ),
        )

    spread = min(
        10,
        max(2, remaining),
    )

    start = (
        needed_average - spread / 2
    )

    end = (
        needed_average + spread / 2
    )

    values = []

    for index in range(remaining):

        fraction = (
            index / (remaining - 1)
        )

        value = (
            start
            + (end - start) * fraction
        )

        values.append(
            max(
                0,
                math.ceil(value),
            )
        )

    return tuple(values)


def build_falling_path(
    needed_average: float,
    remaining: int,
) -> tuple[int, ...]:
    """Create a path that starts stronger and eases later."""

    return tuple(
        reversed(
            build_rising_path(
                needed_average,
                remaining,
            )
        )
    )


def build_buffer_path(
    needed_average: float,
    remaining: int,
) -> tuple[int, ...]:
    """Create a path slightly above the minimum needed."""

    score = max(
        0,
        math.ceil(
            needed_average + 3
        ),
    )

    return tuple(
        score
        for _ in range(remaining)
    )


def generate_grade_paths(
    grades: list[float],
    target: float,
    remaining: int,
    extra_credit_points: float = 0,
    allow_over_100: bool = False,
) -> list[tuple[int, ...]]:
    """Generate practical grade paths for any number of assignments."""

    if remaining <= 0:
        return []

    needed_average = calculate_required_grade(
        grades,
        target,
        remaining,
        extra_credit_points,
    )

    maximum_score = (
        110
        if allow_over_100
        else 100
    )

    if needed_average > maximum_score:
        return []

    if needed_average <= 0:
        return [
            tuple(
                0
                for _ in range(remaining)
            )
        ]

    candidates = [
        build_even_path(
            needed_average,
            remaining,
        ),
        build_rising_path(
            needed_average,
            remaining,
        ),
        build_falling_path(
            needed_average,
            remaining,
        ),
        build_buffer_path(
            needed_average,
            remaining,
        ),
    ]

    successful_paths: list[
        tuple[int, ...]
    ] = []

    for path in candidates:

        capped_path = tuple(
            min(score, maximum_score)
            for score in path
        )

        final_average = calculate_average(
            grades + list(capped_path),
            extra_credit_points,
        )

        if (
            final_average >= target
            and capped_path not in successful_paths
        ):
            successful_paths.append(
                capped_path
            )

    return successful_paths


def export_result(
    name: str,
    grades: list[float],
    extra_credit_points: float = 0,
    output_file: str = "grade_report.csv",
) -> Path:
    """Export student results to a CSV file."""

    average = calculate_average(
        grades,
        extra_credit_points,
    )

    path = Path(output_file)

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "Student",
                "Grades",
                "Extra Credit",
                "Average",
                "Letter Grade",
            ]
        )

        writer.writerow(
            [
                name,
                "; ".join(
                    f"{grade:g}"
                    for grade in grades
                ),
                f"{extra_credit_points:g}",
                f"{average:.2f}",
                letter_grade(average),
            ]
        )

    return path


class GradeCalculatorApp:
    """Graphical interface for the Student Grade Calculator."""

    def __init__(
        self,
        root: tk.Tk,
    ) -> None:

        self.root = root

        self.current_grades: list[
            float
        ] = []

        self.dark_mode = False
        self.large_text = False

        self.language = tk.StringVar(
            value="English"
        )

        self.allow_extra_credit = tk.BooleanVar(
            value=False
        )

        self.large_text_var = tk.BooleanVar(
            value=False
        )

        self.load_preferences()

        self.root.geometry(
            "800x1080"
        )

        self.root.minsize(
            650,
            750,
        )

        self.create_interface()

        self.apply_language()
        self.apply_theme()
        self.apply_large_text()

        self.root.bind(
            "<Control-Return>",
            lambda event: self.calculate(),
        )

        self.root.bind(
            "<Control-e>",
            lambda event: self.export(),
        )

        self.root.bind(
            "<Control-r>",
            lambda event: self.clear(),
        )

        self.name_entry.focus()


    def create_interface(self) -> None:
        """Create all interface components."""

        self.top_frame = tk.Frame(
            self.root
        )

        self.top_frame.pack(
            fill="x",
            padx=20,
            pady=10,
        )

        self.language_label = tk.Label(
            self.top_frame,
            text="Language:",
        )

        self.language_label.pack(
            side="left"
        )

        self.language_menu = ttk.Combobox(
            self.top_frame,
            textvariable=self.language,
            values=list(
                LANGUAGES.keys()
            ),
            state="readonly",
            width=12,
        )

        self.language_menu.pack(
            side="left",
            padx=5,
        )

        self.language_menu.bind(
            "<<ComboboxSelected>>",
            self.change_language,
        )

        self.dark_mode_button = tk.Button(
            self.top_frame,
            text="Dark Mode",
            command=self.toggle_dark_mode,
        )

        self.dark_mode_button.pack(
            side="right",
            padx=5,
        )

        self.large_text_check = tk.Checkbutton(
            self.top_frame,
            text="Larger Text",
            variable=self.large_text_var,
            command=self.toggle_large_text,
        )

        self.large_text_check.pack(
            side="right",
            padx=5,
        )

        self.title_label = tk.Label(
            self.root,
            font=(
                "Arial",
                22,
                "bold",
            ),
        )

        self.title_label.pack(
            pady=(10, 2)
        )

        self.subtitle_label = tk.Label(
            self.root,
            font=(
                "Arial",
                11,
                "italic",
            ),
        )

        self.subtitle_label.pack(
            pady=(0, 4)
        )

        self.beta_label = tk.Label(
            self.root,
            text=f"{APP_VERSION} • {APP_BUILD_LABEL}",
            font=("Arial", 9, "bold"),
        )

        self.beta_label.pack(
            pady=(0, 8)
        )

        self.instructions_label = tk.Label(
            self.root,
            justify="center",
        )

        self.instructions_label.pack(
            pady=5
        )

        self.name_label = tk.Label(
            self.root
        )

        self.name_label.pack()

        self.name_entry = tk.Entry(
            self.root,
            width=45,
        )

        self.name_entry.pack(
            pady=5
        )

        self.grades_label = tk.Label(
            self.root
        )

        self.grades_label.pack()

        self.grades_entry = tk.Entry(
            self.root,
            width=45,
        )

        self.grades_entry.pack(
            pady=5
        )

        self.extra_credit_checkbox = tk.Checkbutton(
            self.root,
            variable=self.allow_extra_credit,
        )

        self.extra_credit_checkbox.pack(
            pady=3
        )

        self.extra_points_label = tk.Label(
            self.root
        )

        self.extra_points_label.pack()

        self.extra_points_entry = tk.Entry(
            self.root,
            width=20,
        )

        self.extra_points_entry.insert(
            0,
            "0",
        )

        self.extra_points_entry.pack(
            pady=3
        )

        self.calculate_button = tk.Button(
            self.root,
            command=self.calculate,
        )

        self.calculate_button.pack(
            pady=10
        )

        self.result_label = tk.Label(
            self.root,
            text=(
                "Average: --\n"
                "Letter Grade: --"
            ),
            font=(
                "Arial",
                14,
                "bold",
            ),
        )

        self.result_label.pack(
            pady=8
        )

        self.progress_title = tk.Label(
            self.root,
            font=(
                "Arial",
                11,
                "bold",
            ),
        )

        self.progress_title.pack()

        self.feedback_label = tk.Label(
            self.root,
            text="",
            wraplength=600,
            justify="center",
        )

        self.feedback_label.pack(
            pady=5
        )

        self.separator = ttk.Separator(
            self.root,
            orient="horizontal",
        )

        self.separator.pack(
            fill="x",
            padx=60,
            pady=10,
        )

        self.target_label = tk.Label(
            self.root
        )

        self.target_label.pack()

        self.target_entry = tk.Entry(
            self.root,
            width=20,
        )

        self.target_entry.pack(
            pady=3
        )

        self.remaining_label = tk.Label(
            self.root
        )

        self.remaining_label.pack()

        self.remaining_entry = tk.Entry(
            self.root,
            width=20,
        )

        self.remaining_entry.pack(
            pady=3
        )

        self.goal_button = tk.Button(
            self.root,
            command=self.calculate_goal,
        )

        self.goal_button.pack(
            pady=6
        )

        self.goal_label = tk.Label(
            self.root,
            text="",
            wraplength=600,
            justify="center",
        )

        self.goal_label.pack(
            pady=5
        )

        self.path_button = tk.Button(
            self.root,
            command=self.show_grade_paths,
        )

        self.path_button.pack(
            pady=5
        )

        self.bottom_frame = tk.Frame(
            self.root
        )

        self.bottom_frame.pack(
            pady=10
        )

        self.export_button = tk.Button(
            self.bottom_frame,
            command=self.export,
        )

        self.export_button.pack(
            side="left",
            padx=5,
        )

        self.clear_button = tk.Button(
            self.bottom_frame,
            command=self.clear,
        )

        self.clear_button.pack(
            side="left",
            padx=5,
        )

        self.shortcut_label = tk.Label(
            self.root,
            text=(
                "Keyboard shortcuts: "
                "Ctrl+Enter = Calculate | "
                "Ctrl+E = Export | "
                "Ctrl+R = Reset"
            ),
            font=("Arial", 9),
        )

        self.shortcut_label.pack(
            pady=(4, 2)
        )

        self.feedback_build_label = tk.Label(
            self.root,
            text="Beta build for teacher feedback — calculations should be reviewed before high-stakes use.",
            font=("Arial", 8, "italic"),
            wraplength=650,
            justify="center",
        )

        self.feedback_build_label.pack(
            pady=(0, 6)
        )


    def get_extra_credit_points(
        self
    ) -> float:
        """Validate standalone extra-credit points."""

        raw_value = (
            self.extra_points_entry
            .get()
            .strip()
        )

        if not raw_value:
            return 0

        try:
            points = float(
                raw_value
            )

        except ValueError as exc:
            raise ValueError(
                "Extra credit points must be a number."
            ) from exc

        if points < 0:
            raise ValueError(
                "Extra credit points cannot be negative."
            )

        return points


    def calculate(self) -> None:
        """Validate input and display grade results."""

        language = LANGUAGES[
            self.language.get()
        ]

        name = (
            self.name_entry
            .get()
            .strip()
        )

        if not name:
            messagebox.showerror(
                "Missing Name",
                language[
                    "missing_name"
                ],
            )
            return

        try:
            grades = parse_grades(
                self.grades_entry.get(),
                self.allow_extra_credit.get(),
            )

            extra_points = (
                self.get_extra_credit_points()
            )

            average = calculate_average(
                grades,
                extra_points,
            )

        except ValueError as error:
            messagebox.showerror(
                language[
                    "invalid_grades"
                ],
                str(error),
            )
            return

        self.current_grades = grades

        self.result_label.config(
            text=(
                f"{language['average']}: "
                f"{average:.2f}%\n"
                f"{language['letter_grade']}: "
                f"{letter_grade(average)}"
            )
        )

        self.feedback_label.config(
            text=progress_feedback(
                average
            )
        )


    def calculate_goal(self) -> None:
        """Calculate grades needed to reach a target."""

        language = LANGUAGES[
            self.language.get()
        ]

        if not self.current_grades:

            messagebox.showerror(
                "Calculate Grades First",
                language[
                    "calculate_first"
                ],
            )

            return

        try:
            target = float(
                self.target_entry.get()
            )

            remaining = int(
                self.remaining_entry.get()
            )

            extra_points = (
                self.get_extra_credit_points()
            )

            needed = calculate_required_grade(
                self.current_grades,
                target,
                remaining,
                extra_points,
            )

            current_average = calculate_average(
                self.current_grades,
                extra_points,
            )

        except ValueError as error:

            messagebox.showerror(
                "Invalid Goal Information",
                str(error),
            )

            return

        if needed > 100:

            if self.allow_extra_credit.get():

                result = (
                    f"You need an average of "
                    f"{needed:.2f}% on the "
                    "remaining assignments.\n"
                    "This may be possible if "
                    "extra-credit grades above "
                    "100 are available."
                )

            else:

                result = (
                    f"You would need an average "
                    f"of {needed:.2f}%.\n"
                    "The target is not achievable "
                    "with standard grades capped "
                    "at 100."
                )

        elif needed < 0:

            result = (
                "You have already secured your "
                "target average based on the "
                "entered information."
            )

        else:

            result = (
                f"You need an average of "
                f"{needed:.2f}% on the "
                f"remaining {remaining} "
                "assignment(s)."
            )

        self.goal_label.config(
            text=result
        )

        self.feedback_label.config(
            text=progress_feedback(
                current_average,
                target,
            )
        )


    def show_grade_paths(self) -> None:
        """Display practical grade paths for the target."""

        if not self.current_grades:

            messagebox.showerror(
                "Calculate Grades First",
                "Please calculate your current "
                "grade first.",
            )

            return

        try:
            target = float(
                self.target_entry.get()
            )

            remaining = int(
                self.remaining_entry.get()
            )

            if remaining <= 0:
                raise ValueError(
                    "Remaining assignments must "
                    "be greater than zero."
                )

            if not 0 <= target <= 100:
                raise ValueError(
                    "Target grade must be "
                    "between 0 and 100."
                )

            extra_points = (
                self.get_extra_credit_points()
            )

            needed = calculate_required_grade(
                self.current_grades,
                target,
                remaining,
                extra_points,
            )

        except ValueError as error:

            messagebox.showerror(
                "Invalid Goal Information",
                str(error),
            )

            return

        path_window = tk.Toplevel(
            self.root
        )

        path_window.title(
            "Grade Path Planning"
        )

        path_window.geometry(
            "650x600"
        )

        if self.dark_mode:
            path_background = "#242424"
            path_foreground = "#ffffff"

        else:
            path_background = "#f0f0f0"
            path_foreground = "#000000"

        path_window.configure(
            bg=path_background
        )

        heading = tk.Label(
            path_window,
            text="Grade Path Planning",
            font=(
                "Arial",
                18,
                "bold",
            ),
            bg=path_background,
            fg=path_foreground,
        )

        heading.pack(
            pady=15
        )

        summary = tk.Label(
            path_window,
            text=(
                f"Target Average: "
                f"{target:.2f}%\n"
                f"Remaining Assignments: "
                f"{remaining}\n"
                f"Average Needed: "
                f"{needed:.2f}%"
            ),
            font=(
                "Arial",
                12,
            ),
            bg=path_background,
            fg=path_foreground,
        )

        summary.pack(
            pady=5
        )

        paths = generate_grade_paths(
            self.current_grades,
            target,
            remaining,
            extra_points,
            self.allow_extra_credit.get(),
        )

        if paths:

            labels = [
                "Consistent Path",
                "Strong Finish",
                "Strong Start",
                "Buffer Path",
            ]

            lines = [
                "Possible grade paths:",
                "",
            ]

            for index, path in enumerate(
                paths
            ):

                label = (
                    labels[index]
                    if index < len(labels)
                    else f"Path {index + 1}"
                )

                formatted = ", ".join(
                    f"{score}%"
                    for score in path
                )

                lines.append(
                    f"{label}:"
                )

                lines.append(
                    formatted
                )

                lines.append("")

            information = "\n".join(
                lines
            )

        else:

            maximum_score = (
                110
                if self.allow_extra_credit.get()
                else 100
            )

            if needed > maximum_score:

                information = (
                    f"You would need an average "
                    f"of {needed:.2f}% on the "
                    "remaining assignments.\n\n"
                    f"The current maximum allowed "
                    f"score is {maximum_score}%, "
                    "so no achievable grade path "
                    "is available."
                )

            else:

                information = (
                    "No grade path could be "
                    "generated for the entered values."
                )

        results = tk.Label(
            path_window,
            text=information,
            justify="left",
            wraplength=580,
            bg=path_background,
            fg=path_foreground,
        )

        results.pack(
            padx=20,
            pady=20,
        )


    def export(self) -> None:
        """Export the current calculation to CSV."""

        language = LANGUAGES[
            self.language.get()
        ]

        if not self.current_grades:

            messagebox.showerror(
                "No Results",
                language[
                    "no_results"
                ],
            )

            return

        try:

            extra_points = (
                self.get_extra_credit_points()
            )

            path = export_result(
                self.name_entry
                .get()
                .strip(),
                self.current_grades,
                extra_points,
            )

        except ValueError as error:

            messagebox.showerror(
                "Export Error",
                str(error),
            )

            return

        messagebox.showinfo(
            language[
                "export_complete"
            ],
            f"Results saved to:\n"
            f"{path.resolve()}",
        )


    def clear(self) -> None:
        """Reset all interface fields."""

        self.name_entry.delete(
            0,
            tk.END,
        )

        self.grades_entry.delete(
            0,
            tk.END,
        )

        self.target_entry.delete(
            0,
            tk.END,
        )

        self.remaining_entry.delete(
            0,
            tk.END,
        )

        self.extra_points_entry.delete(
            0,
            tk.END,
        )

        self.extra_points_entry.insert(
            0,
            "0",
        )

        self.allow_extra_credit.set(
            False
        )

        self.current_grades = []

        language = LANGUAGES[
            self.language.get()
        ]

        self.result_label.config(
            text=(
                f"{language['average']}: --\n"
                f"{language['letter_grade']}: --"
            )
        )

        self.goal_label.config(
            text=""
        )

        self.feedback_label.config(
            text=""
        )

        self.name_entry.focus()


    def change_language(
        self,
        event=None,
    ) -> None:
        """Change the interface language."""

        self.apply_language()
        self.save_preferences()


    def apply_language(self) -> None:
        """Apply translated interface text."""

        language = LANGUAGES[
            self.language.get()
        ]

        self.root.title(
            f"{APP_NAME} — {APP_VERSION}"
        )

        self.title_label.config(
            text=language["title"]
        )

        self.subtitle_label.config(
            text=language[
                "subtitle"
            ]
        )

        self.instructions_label.config(
            text=language[
                "instructions"
            ]
        )

        self.language_label.config(
            text=language[
                "language"
            ]
        )

        self.name_label.config(
            text=language[
                "student_name"
            ]
        )

        self.grades_label.config(
            text=language[
                "grades"
            ]
        )

        self.extra_credit_checkbox.config(
            text=language[
                "allow_extra_credit"
            ]
        )

        self.extra_points_label.config(
            text=language[
                "extra_credit_points"
            ]
        )

        self.calculate_button.config(
            text=language[
                "calculate"
            ]
        )

        self.progress_title.config(
            text=language[
                "progress"
            ]
        )

        self.target_label.config(
            text=language[
                "desired_grade"
            ]
        )

        self.remaining_label.config(
            text=language[
                "remaining"
            ]
        )

        self.goal_button.config(
            text=language[
                "goal"
            ]
        )

        self.path_button.config(
            text=language[
                "path"
            ]
        )

        self.export_button.config(
            text=language[
                "export"
            ]
        )

        self.clear_button.config(
            text=language[
                "clear"
            ]
        )

        self.large_text_check.config(
            text=language[
                "large_text"
            ]
        )

        self.update_theme_button_text()

        if not self.current_grades:

            self.result_label.config(
                text=(
                    f"{language['average']}: --\n"
                    f"{language['letter_grade']}: --"
                )
            )


    def toggle_dark_mode(self) -> None:
        """Switch between light and dark mode."""

        self.dark_mode = (
            not self.dark_mode
        )

        self.apply_theme()
        self.save_preferences()


    def apply_theme(self) -> None:
        """Apply the current theme."""

        if self.dark_mode:

            background = "#242424"
            foreground = "#ffffff"
            entry_background = "#3b3b3b"
            button_background = "#4a4a4a"

        else:

            background = "#f0f0f0"
            foreground = "#000000"
            entry_background = "#ffffff"
            button_background = "#e7e7e7"

        self.root.configure(
            bg=background
        )

        # Keep any already-open Grade Path Planning/Toplevel windows
        # synchronized when the user toggles light/dark mode.
        for window in self.root.winfo_children():
            if isinstance(window, tk.Toplevel):
                try:
                    window.configure(bg=background)
                except tk.TclError:
                    pass

        style = ttk.Style()

        try:
            style.theme_use(
                "clam"
            )

        except tk.TclError:
            pass

        style.configure(
            "TSeparator",
            background=foreground,
        )

        style.configure(
            "TCombobox",
            fieldbackground=entry_background,
            background=entry_background,
            foreground=foreground,
        )

        self.apply_theme_to_widget(
            self.root,
            background,
            foreground,
            entry_background,
            button_background,
        )

        # Toplevel windows are not children returned by the recursive
        # theme walk in every Tk configuration, so explicitly refresh them.
        for window in self.root.winfo_children():
            if isinstance(window, tk.Toplevel):
                self.apply_theme_to_widget(
                    window,
                    background,
                    foreground,
                    entry_background,
                    button_background,
                )

        self.update_theme_button_text()


    def apply_theme_to_widget(
        self,
        widget,
        background: str,
        foreground: str,
        entry_background: str,
        button_background: str,
    ) -> None:
        """Safely apply colors to supported Tk widgets."""

        for child in widget.winfo_children():

            if isinstance(
                child,
                ttk.Widget,
            ):

                self.apply_theme_to_widget(
                    child,
                    background,
                    foreground,
                    entry_background,
                    button_background,
                )

                continue

            try:

                if isinstance(
                    child,
                    tk.Frame,
                ):
                    child.configure(
                        bg=background
                    )

                elif isinstance(
                    child,
                    tk.Label,
                ):
                    child.configure(
                        bg=background,
                        fg=foreground,
                    )

                elif isinstance(
                    child,
                    tk.Entry,
                ):
                    child.configure(
                        bg=entry_background,
                        fg=foreground,
                        insertbackground=foreground,
                    )

                elif isinstance(
                    child,
                    tk.Button,
                ):
                    child.configure(
                        bg=button_background,
                        fg=foreground,
                        activebackground=button_background,
                        activeforeground=foreground,
                    )

                elif isinstance(
                    child,
                    tk.Checkbutton,
                ):
                    child.configure(
                        bg=background,
                        fg=foreground,
                        activebackground=background,
                        activeforeground=foreground,
                        selectcolor=entry_background,
                    )

            except tk.TclError:
                pass

            self.apply_theme_to_widget(
                child,
                background,
                foreground,
                entry_background,
                button_background,
            )


    def update_theme_button_text(
        self
    ) -> None:
        """Update the dark/light mode button text."""

        language = LANGUAGES[
            self.language.get()
        ]

        if self.dark_mode:

            self.dark_mode_button.config(
                text=language[
                    "light"
                ]
            )

        else:

            self.dark_mode_button.config(
                text=language[
                    "dark"
                ]
            )


    def toggle_large_text(self) -> None:
        """Toggle larger interface text."""

        self.large_text = (
            self.large_text_var.get()
        )

        self.apply_large_text()
        self.save_preferences()


    def apply_large_text(self) -> None:
        """Apply the selected text size."""

        if self.large_text:

            normal_size = 12
            button_size = 12
            title_size = 26
            result_size = 17

        else:

            normal_size = 10
            button_size = 10
            title_size = 22
            result_size = 14

        for widget in (
            self.root.winfo_children()
        ):

            self.apply_font_size(
                widget,
                normal_size,
                button_size,
            )

        self.title_label.config(
            font=(
                "Arial",
                title_size,
                "bold",
            )
        )

        self.result_label.config(
            font=(
                "Arial",
                result_size,
                "bold",
            )
        )

        self.progress_title.config(
            font=(
                "Arial",
                normal_size + 1,
                "bold",
            )
        )


    def apply_font_size(
        self,
        widget,
        normal_size: int,
        button_size: int,
    ) -> None:
        """Apply font sizes recursively."""

        if isinstance(
            widget,
            (
                tk.Label,
                tk.Entry,
                tk.Checkbutton,
            ),
        ):

            try:

                widget.configure(
                    font=(
                        "Arial",
                        normal_size,
                    )
                )

            except tk.TclError:
                pass

        elif isinstance(
            widget,
            tk.Button,
        ):

            try:

                widget.configure(
                    font=(
                        "Arial",
                        button_size,
                    )
                )

            except tk.TclError:
                pass

        for child in (
            widget.winfo_children()
        ):

            self.apply_font_size(
                child,
                normal_size,
                button_size,
            )


    def save_preferences(self) -> None:
        """Save interface preferences."""

        preferences = {
            "dark_mode": self.dark_mode,
            "language": self.language.get(),
            "large_text": self.large_text_var.get(),
        }

        try:

            with PREFERENCES_FILE.open(
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    preferences,
                    file,
                    indent=4,
                )

        except OSError:
            pass


    def load_preferences(self) -> None:
        """Load saved interface preferences."""

        if not PREFERENCES_FILE.exists():
            return

        try:

            with PREFERENCES_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:

                preferences = json.load(
                    file
                )

            self.dark_mode = (
                preferences.get(
                    "dark_mode",
                    False,
                )
            )

            saved_language = (
                preferences.get(
                    "language",
                    "English",
                )
            )

            if saved_language in LANGUAGES:

                self.language.set(
                    saved_language
                )

            self.large_text = (
                preferences.get(
                    "large_text",
                    False,
                )
            )

            self.large_text_var.set(
                self.large_text
            )

        except (
            OSError,
            json.JSONDecodeError,
        ):
            pass


def main() -> None:
    """Start the Student Grade Calculator."""

    root = tk.Tk()

    GradeCalculatorApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()