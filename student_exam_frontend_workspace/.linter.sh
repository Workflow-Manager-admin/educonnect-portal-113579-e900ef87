#!/bin/bash
cd /home/kavia/workspace/code-generation/educonnect-portal-113579-e900ef87/student_exam_frontend_workspace/student_exam_frontend
npm run build
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
   exit 1
fi

