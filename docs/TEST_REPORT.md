# Test Report

Date: 2026-04-29
Project: TalentRank Studio
Workspace: D:/6th sem/Software_Engineering/Project/softwareengineering

## Summary

- Overall status: PASS
- Automated tests: 12 passed, 0 failed
- Latest run time: 0.58s
- Python environment: .venv (Python 3.12.3)

## Test Execution

Command used:

```powershell
$env:PYTHONPATH='src'; & "d:/6th sem/Software_Engineering/Project/softwareengineering/.venv/Scripts/python.exe" -m pytest -q
```

Observed output:

```text
............                                                             [100%]
12 passed in 0.58s
```

## Destructive Testing Performed

Purpose: Validate resilience against corrupted resume uploads and verify graceful failure behavior.

Scenarios executed:

1. Corrupted PDF upload to /v1/preview-files
- Expected: Request does not crash; response marks file as error.
- Result: PASS (HTTP 200 with preview status="error")

2. Corrupted DOCX upload to /v1/preview-files
- Expected: Request does not crash; response marks file as error.
- Result: PASS

3. Corrupted PDF upload to /v1/analyze-files
- Expected: Request rejected with clear client error.
- Result: PASS (HTTP 400 with error detail)

## Fix Validation Included

The following resilience fixes were validated by tests:

- Parser now converts corrupted PDF parsing failures into controlled ResumeParsingError.
- Parser now converts corrupted DOCX parsing failures into controlled ResumeParsingError.
- API endpoints now return handled responses for malformed upload content instead of bubbling parser exceptions.

## Files Updated During Test Hardening

- src/app/services/resume_parser.py
- tests/test_resume_parser.py
- tests/test_preview_files.py

## Risk Notes

- Underlying PDF library still logs malformed file warnings to stderr for invalid PDFs. This does not break API behavior but can increase log noise.
- Additional stress testing is recommended for max-size files, mixed valid+invalid multi-file batches, and concurrent upload load.
