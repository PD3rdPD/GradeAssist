"""Shared calculation logic for the Student Grade Calculator."""

from __future__ import annotations

import math


def calculate_average(
    grades: list[float],
    extra_credit_points: float = 0,
) -> float:
    """Calculate the average with optional extra-credit points."""

    if not grades:
        raise ValueError("At least one grade is required.")

    return (sum(grades) + extra_credit_points) / len(grades)



def calculate_weighted_average(
    categories: list[tuple[list[float], float]],
) -> float:
    """Calculate an overall average using weighted grade categories."""

    if not categories:
        raise ValueError("At least one grade category is required.")

    total_weight = 0.0
    weighted_total = 0.0

    for grades, weight in categories:
        if not grades:
            raise ValueError(
                "Each category must contain at least one grade."
            )

        if weight < 0:
            raise ValueError(
                "Category weights cannot be negative."
            )

        category_average = sum(grades) / len(grades)

        weighted_total += (
            category_average * (weight / 100)
        )

        total_weight += weight

    if abs(total_weight - 100) > 0.01:
        raise ValueError(
            "Category weights must total 100%."
        )

    return weighted_total

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
            raise ValueError(
                "Grades cannot contain blank entries."
            )

        try:
            grade = float(item)

        except ValueError as exc:
            raise ValueError(
                f"'{item}' is not a valid number."
            ) from exc

        if grade < 0:
            raise ValueError(
                "Grades cannot be negative."
            )

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
        raise ValueError(
            "At least one current grade is required."
        )

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
    """Generate grade-progress feedback."""

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
    """Create a consistent-score grade path."""

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

    values: list[int] = []

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
    """Generate practical grade paths for remaining assignments."""

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
