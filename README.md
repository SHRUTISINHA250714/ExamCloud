# ExamCloud

**A serverless online examination system built with **AWS** Lambda, **API** Gateway, and DynamoDB.**

ExamCloud allows students to take online exams, receive instant answer feedback, and view their final scores. The backend runs on **AWS** Lambda and communicates with the frontend through Amazon **API** Gateway, while Amazon DynamoDB stores exam questions and student attempts.

## The Idea

Traditional examination systems often require application servers to be deployed and maintained. ExamCloud demonstrates an alternative using **AWS** serverless services, where backend functions execute on demand without requiring you to manage servers.

Students can start an exam, answer questions, receive immediate feedback, and submit their attempts for automatic scoring.

## What It Does

- Retrieves exam questions from a backend **API**.
- Keeps correct answers out of the question-retrieval **API** response.
- Validates multiple-choice and short-answer responses.
- Provides immediate feedback for correct and incorrect answers.
- Highlights correct answers in green and incorrect selections in red.
- Calculates final scores and saves exam attempts.
- Supports dynamically configured exams, including a five-question **AWS** Fundamentals quiz.

## How It's Built

| Component | Technology | Purpose |
|---|---|---|
| Frontend | HTML, CSS, JavaScript | Exam interface, answer selection, feedback, and results |
| API layer | Amazon API Gateway | Exposes HTTPS endpoints to the frontend |
| Backend logic | AWS Lambda | Retrieves questions, checks answers, and submits exams |
| Database | Amazon DynamoDB | Stores exams, answer keys, and exam attempts |
| Access control | AWS IAM | Controls Lambda permissions to access DynamoDB |

## Architecture

```text
Student
    |
    v
### Web Frontend
(**HTML**, **CSS**, JavaScript)
    |
    v
Amazon **API** Gateway
    |
    +---------------------------+
    |             |             |
    v             v             v
getQuestions  checkAnswer  submitExam
    |             |             |
    +-------------+-------------+
    |
    v
    Amazon DynamoDB
    - Exams
    - Attempts
```

## Backend API Endpoints

| Method | Endpoint | Function |
|---|---|---|
| GET | `/exams/{examId}/questions` | Retrieves exam questions without exposing answer keys |
| POST | `/exams/{examId}/answer` | Checks an individual answer and returns feedback |
| POST | `/exams/{examId}/submit` | Grades the submitted exam and records the result |

The answer-checking endpoint supports immediate feedback during the quiz. The final submission endpoint calculates and persists the overall exam result.

## Database Design

ExamCloud uses two Amazon DynamoDB tables.

### Exams

Stores exam metadata and questions, including question IDs, text, options, question types, and correct answers.

### Attempts

Stores student exam submissions and their results, including scores and question-level grading information as implemented by the backend.

## Implementation Workflow

1. **Database setup:** Created the `Exams` and `Attempts` tables in DynamoDB.
2. **Question retrieval:** Implemented `getQuestions` to retrieve exam data and remove answer keys before returning questions.
3. **Answer validation:** Implemented `checkAnswer` to validate multiple-choice and short-answer responses.
4. **Exam submission:** Implemented `submitExam` to grade submissions and save results.
5. ****API** integration:** Connected the Lambda functions to Amazon **API** Gateway and configured **CORS** for frontend requests.
6. **Frontend development:** Built the exam interface with question navigation, answer selection, immediate feedback, and final score display.
7. **End-to-end testing:** Tested question retrieval, answer validation, and final exam submission.

## Security Considerations

- Correct answers are removed from the question-retrieval **API** response.
- **IAM** roles control access to DynamoDB.
- **API** Gateway provides **HTTPS** endpoints for communication with the frontend.
- **CORS** is configured to support frontend **API** requests.

**Note:** Authentication, authorization of individual students, and additional anti-cheating controls would be needed before using the system for high-stakes examinations.

## Why Serverless?

- No **EC2** instances or application servers to manage.
- Backend functions execute on demand.
- **AWS** manages the underlying compute infrastructure.
- DynamoDB provides a managed database service.
- Usage-based pricing can be economical for small applications, although charges depend on configuration and usage.

## Current Deployment

- **Backend:** **AWS** Lambda, Amazon **API** Gateway, and Amazon DynamoDB in the Asia Pacific (Sydney) region.
- **Frontend:** **HTML**, **CSS**, and JavaScript, currently runnable locally through a development server.

The frontend can be hosted separately on a static hosting platform to make the complete application accessible through a public **URL**.

## Future Improvements

- Student authentication and role-based access.
- Instructor dashboard for creating and managing exams.
- Exam timers and automatic submission when time expires.
- Exam history and performance analytics.
- Public frontend deployment using Amazon S3 and CloudFront or another static hosting platform.
- Automated testing and CI/CD deployment.

## License

This project can be distributed under the **MIT** License if an **MIT** license file is added and all included code is appropriately licensed.

