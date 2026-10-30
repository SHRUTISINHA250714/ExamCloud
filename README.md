# ExamCloud – Serverless Online Examination System

A serverless online examination system built using **AWS Lambda, Amazon API Gateway, DynamoDB, and Amazon S3**.

ExamCloud allows students to take online exams, receive instant answer feedback, and view their final scores. The backend runs on AWS Lambda and communicates with the frontend through Amazon API Gateway, while Amazon DynamoDB stores exam questions and student attempts. The frontend is deployed using Amazon S3 Static Website Hosting, making the application accessible through a public URL.

## The Idea

Traditional examination systems often require application servers to be deployed, maintained, and scaled. ExamCloud demonstrates an alternative using AWS serverless services, where backend functions execute on demand without requiring server management.

Students can start an exam, answer questions, receive immediate feedback, and submit their attempts for automatic scoring.

## What It Does

- Retrieves exam questions from a backend API.
- Keeps correct answers out of the question-retrieval API response.
- Validates multiple-choice and short-answer responses.
- Provides immediate feedback for correct and incorrect answers.
- Highlights correct answers in green and incorrect selections in red.
- Calculates final scores and saves exam attempts.
- Supports dynamically configured exams, including a five-question AWS Fundamentals quiz.
- Provides public frontend access through Amazon S3 Static Website Hosting.

## How It's Built

| Component | Technology | Purpose |
|---|---|---|
| Frontend | HTML, CSS, JavaScript | Exam interface, answer selection, feedback, and results |
| Frontend Hosting | Amazon S3 | Stores and hosts static website files |
| API Layer | Amazon API Gateway | Exposes HTTPS endpoints to the frontend |
| Backend Logic | AWS Lambda (Python) | Retrieves questions, checks answers, and submits exams |
| Database | Amazon DynamoDB | Stores exams, answer keys, and exam attempts |
| Access Control | AWS IAM | Controls Lambda permissions to access DynamoDB |

## Architecture

```text
                 Student (Browser)
                        |
                        v
                 Amazon S3 Bucket
                (Static Website Hosting)
                        |
                        | HTTPS API Requests
                        v
                Amazon API Gateway
                        |
             +----------+----------+
             |          |          |
             v          v          v
        getQuestions checkAnswer submitExam
             |          |          |
             +----------+----------+
                        |
                        v
                 Amazon DynamoDB
                  |           |
                  v           v
                Exams      Attempts
```

**Architecture overview:**

1. Amazon S3 hosts the static frontend files (HTML, CSS, JavaScript).
2. Students access the application through the S3 website endpoint.
3. The frontend communicates with API Gateway through HTTPS requests.
4. API Gateway invokes the appropriate Lambda function.
5. Lambda functions retrieve or update data in DynamoDB.

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

1. **Database Setup:** Created the `Exams` and `Attempts` tables in Amazon DynamoDB.
2. **Question Retrieval:** Implemented `getQuestions` to retrieve exam data and remove answer keys before returning questions.
3. **Answer Validation:** Implemented `checkAnswer` to validate multiple-choice and short-answer responses.
4. **Exam Submission:** Implemented `submitExam` to grade submissions and save results.
5. **API Integration:** Connected the Lambda functions to Amazon API Gateway and configured CORS for frontend requests.
6. **Frontend Development:** Built the exam interface with question navigation, answer selection, immediate feedback, and final score display.
7. **S3 Bucket Creation:** Created an Amazon S3 general-purpose bucket in the Asia Pacific (Sydney) region.
8. **Frontend Deployment:** Uploaded `index.html` and enabled S3 Static Website Hosting with `index.html` as the index document.
9. **Bucket Permissions:** Configured a bucket policy to allow public read access to website objects.
10. **End-to-End Testing:** Tested question retrieval, answer validation, final exam submission, and public website accessibility.

## Security Considerations

- Correct answers are removed from the question-retrieval API response.
- IAM roles control Lambda access to DynamoDB.
- API Gateway provides HTTPS endpoints for backend communication.
- CORS is configured to support frontend API requests.
- S3 bucket policies control public access to frontend objects.
- Only intentionally public frontend files are stored in the publicly readable bucket.

**Note:** Authentication, authorization of individual students, and additional anti-cheating controls would be needed before using the system for high-stakes examinations.

## Why Serverless?

- No EC2 instances or application servers to manage.
- Backend functions execute on demand.
- AWS manages the underlying compute infrastructure.
- DynamoDB provides a managed database service.
- S3 provides managed static website hosting.
- Usage-based pricing can be economical for small applications, although charges depend on configuration and usage.

## Current Deployment

- **Backend:** AWS Lambda, Amazon API Gateway, and Amazon DynamoDB.
- **Backend Region:** Asia Pacific (Sydney) – `ap-southeast-2`.
- **Frontend:** HTML, CSS, and JavaScript hosted on Amazon S3.
- **Frontend Hosting:** S3 Static Website Hosting.
- **Website Endpoint:** [Open ExamCloud](http://serverless-online-exam-shruti.s3-website-ap-southeast-2.amazonaws.com)

The frontend is publicly accessible through the S3 website endpoint, while backend operations are handled through API Gateway and Lambda.

**Note:** S3 static website endpoints support HTTP only. The API Gateway endpoints independently use HTTPS. Amazon CloudFront can be added to provide HTTPS access to the hosted website.

## Future Improvements

- Student authentication and role-based access using Amazon Cognito.
- Instructor dashboard for creating and managing exams.
- Exam timers and automatic submission when time expires.
- Exam history and performance analytics.
- Amazon CloudFront integration for HTTPS delivery, caching, and improved content distribution.
- Restricting direct public S3 access using CloudFront Origin Access Control (OAC).
- Automated testing and CI/CD deployment.

## License

This project can be distributed under the MIT License if an MIT license file is added and all included code is appropriately licensed.
