"""Download and extract code submissions from Google Classroom Docs.

This script uses Google Classroom, Drive, and Docs APIs to fetch student
submissions for a given assignment. It extracts code from the third row of the
first table in each attached Google Docs file and saves the code as a Python
file.
"""

import os
from argparse import ArgumentParser
from pathlib import Path
from typing import List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# OAuth scopes required for Classroom, Drive and Docs read-only access
SCOPES = [
    "https://www.googleapis.com/auth/classroom.coursework.students",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]


def get_credentials() -> Credentials:
    """Load OAuth credentials from token.json or run authorization flow."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        raise RuntimeError(
            "Missing valid credentials. Run Google API authorization "
            "flow first."
        )
    return creds


def read_paragraph_elements(elements: List[dict]) -> str:
    """Concatenate all text in a list of structural elements."""
    text = ""
    for value in elements:
        if "paragraph" in value:
            for elem in value["paragraph"].get("elements", []):
                if "textRun" in elem:
                    text += elem["textRun"].get("content", "")
        elif "table" in value:
            for row in value["table"].get("tableRows", []):
                for cell in row.get("tableCells", []):
                    text += read_paragraph_elements(cell.get("content", []))
    return text


def extract_code_from_doc(document: dict) -> str:
    """Return code text stored in the third row of the first table."""
    for element in document.get("body", {}).get("content", []):
        if "table" not in element:
            continue
        table = element["table"]
        rows = table.get("tableRows", [])
        if len(rows) < 3:
            continue
        row = rows[2]
        code = ""
        for cell in row.get("tableCells", []):
            code += read_paragraph_elements(cell.get("content", []))
        return code.strip()
    return ""


def save_code(text: str, output_dir: Path, filename: str) -> None:
    """Save extracted code text to a .py file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{filename}.py"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def download_codes(
    course_id: str, coursework_id: str, output_dir: Path = Path("codes")
) -> None:
    """Download docs for an assignment and save the extracted code."""
    creds = get_credentials()
    classroom_service = build("classroom", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)

    try:
        submissions = (
            classroom_service.courses()
            .courseWork()
            .studentSubmissions()
            .list(courseId=course_id, courseWorkId=coursework_id)
            .execute()
        )
        for item in submissions.get("studentSubmissions", []):
            attach = (
                item.get("assignmentSubmission", {}).get("attachments", [])
            )
            for file in attach:
                drive_file = file.get("driveFile")
                if not drive_file:
                    continue
                file_id = drive_file["id"]
                file_name = drive_file.get("title", f"submission_{item['id']}")
                doc = (
                    docs_service.documents().get(documentId=file_id).execute()
                )
                code = extract_code_from_doc(doc)
                if code:
                    save_code(code, output_dir, file_name)
    except HttpError as err:
        print(f"API error: {err}")


if __name__ == "__main__":
    parser = ArgumentParser(description="Download code from Classroom Docs")
    parser.add_argument("course_id", help="Classroom course ID")
    parser.add_argument("coursework_id", help="Assignment ID")
    parser.add_argument(
        "--output", default="codes", help="Directory to store downloaded code"
    )
    args = parser.parse_args()

    download_codes(args.course_id, args.coursework_id, Path(args.output))
