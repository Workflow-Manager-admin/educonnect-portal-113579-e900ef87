#!/bin/bash
cd /home/kavia/workspace/code-generation/educonnect-portal-113579-e900ef87/student_exam_api_workspace/student_exam_api
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

