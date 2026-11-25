import csv
from collections import defaultdict
from io import StringIO
from itertools import combinations


def read_choices(text):
    """Return course IDs and a matrix of distinct students shared by each pair."""
    rows = csv.reader(StringIO(text, newline=""), strict=True)
    choices = defaultdict(set)
    try:
        header = next(rows, [])
        header = [value.strip() for value in header]
        if "student_id" not in header or "course_id" not in header:
            raise ValueError("The CSV must include student_id and course_id columns.")
        student_column = header.index("student_id")
        course_column = header.index("course_id")
        for row in rows:
            if not any(value.strip() for value in row):
                continue
            if len(row) != len(header):
                raise ValueError(f"CSV line {rows.line_num} has a different number of columns from the header.")
            student = row[student_column].strip()
            course = row[course_column].strip()
            if not student or not course:
                raise ValueError(f"CSV line {rows.line_num} must contain both IDs.")
            choices[student].add(course)
    except csv.Error as error:
        raise ValueError(f"Invalid CSV near line {rows.line_num}: {error}") from error

    if not choices:
        raise ValueError("The CSV contains no course choices.")
    courses = sorted({course for selected in choices.values() for course in selected})
    indices = {course: index for index, course in enumerate(courses)}
    overlaps = [[0] * len(courses) for _ in courses]
    for selected in choices.values():
        for first, second in combinations(selected, 2):
            a, b = indices[first], indices[second]
            overlaps[a][b] += 1
            overlaps[b][a] += 1
    return courses, overlaps


def find_groups(overlaps, sizes, maximum):
    groups = [[] for _ in sizes]
    courses = sorted(
        range(len(overlaps)),
        key=lambda course: sum(overlap > maximum for overlap in overlaps[course]),
        reverse=True,
    )

    def place(position):
        if position == len(courses):
            return True
        course = courses[position]
        tried_empty_sizes = set()
        for group, size in zip(groups, sizes):
            if len(group) == size or any(overlaps[course][other] > maximum for other in group):
                continue
            if not group:
                if size in tried_empty_sizes:
                    continue
                tried_empty_sizes.add(size)
            group.append(course)
            if place(position + 1):
                return True
            group.pop()
        return False

    return groups if place(0) else None


def solve(overlaps, sizes, cutoff):
    """Minimize the worst pair overlap subject to an exclusive cutoff."""
    if sum(sizes) != len(overlaps):
        raise ValueError(
            f"The group sizes add up to {sum(sizes)}, but the CSV has {len(overlaps)} distinct courses."
        )
    groups = find_groups(overlaps, sizes, cutoff - 1)
    if groups is None:
        return None

    low = 0
    high = max((overlaps[a][b] for group in groups for a, b in combinations(group, 2)), default=0)
    while low < high:
        middle = (low + high) // 2
        candidate = find_groups(overlaps, sizes, middle)
        if candidate is None:
            low = middle + 1
        else:
            groups = candidate
            high = middle
    return [sorted(group) for group in groups]
