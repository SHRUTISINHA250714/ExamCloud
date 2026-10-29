# 1. getQuestions — Retrieve exam questions
# Purpose: Fetches the exam from DynamoDB and removes the correct answers before returning questions to the frontend.

import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-southeast-2"
)
table = dynamodb.Table("Exams")


def json_safe(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError(f"Not serializable: {type(obj).__name__}")


def response(status, data):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(data, default=json_safe)
    }


def lambda_handler(event, context):
    try:
        path = event.get("pathParameters") or {}
        exam_id = path.get("examId")

        if not exam_id:
            return response(400, {"error": "Missing examId"})

        result = table.get_item(Key={"examId": exam_id})
        exam = result.get("Item")

        if not exam:
            return response(404, {"error": "Exam not found"})

        questions = []

        for question in exam.get("questions", []):
            safe_question = {
                key: value
                for key, value in question.items()
                if key not in (
                    "correctAnswerIndex",
                    "correctAnswerText",
                    "correctAnswer"
                )
            }
            questions.append(safe_question)

        return response(200, {
            "examId": exam["examId"],
            "title": exam.get("title", "Online Exam"),
            "duration": exam.get("duration", 10),
            "questions": questions
        })

    except Exception as error:
        print("getQuestions error:", str(error))
        return response(500, {"error": "Internal server error"})
      
# API route: GET /exams/{examId}/questions
# 2. checkAnswer — Check individual answers
# Purpose: Checks each answer immediately and returns whether it is correct. It supports MCQs and short-answer questions.
import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-southeast-2"
)
table = dynamodb.Table("Exams")


def json_safe(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError(f"Not serializable: {type(obj).__name__}")


def response(status, data):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "content-type",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(data, default=json_safe)
    }


def lambda_handler(event, context):
    try:
        method = (
            event.get("requestContext", {})
            .get("http", {})
            .get("method")
        )

        if method == "OPTIONS":
            return response(200, {"message": "OK"})

        path = event.get("pathParameters") or {}
        exam_id = path.get("examId")

        if not exam_id:
            return response(400, {"error": "Missing examId"})

        raw_body = event.get("body") or "{}"
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

        qid = body.get("qId")

        if not qid:
            return response(400, {"error": "Missing qId"})

        result = table.get_item(Key={"examId": exam_id})
        exam = result.get("Item")

        if not exam:
            return response(404, {"error": "Exam not found"})

        question = next(
            (q for q in exam.get("questions", [])
             if q.get("qId") == qid),
            None
        )

        if not question:
            return response(404, {"error": "Question not found"})

        if question.get("type", "mcq") == "short":
            given = body.get("answerText")
            expected = question.get("correctAnswerText")

            if not isinstance(given, str):
                return response(400, {"error": "Invalid answerText"})

            if expected is None:
                return response(500, {"error": "Answer key unavailable"})

            correct = (
                given.strip().casefold()
                == str(expected).strip().casefold()
            )

            return response(200, {
                "qId": qid,
                "correct": correct,
                "correctAnswerText": expected
            })

        given = body.get("answerIndex")
        expected = question.get("correctAnswerIndex")

        if not isinstance(given, int) or isinstance(given, bool):
            return response(400, {"error": "Invalid answerIndex"})

        options = question.get("options", [])

        if given < 0 or given >= len(options):
            return response(400, {"error": "Answer index out of range"})

        if expected is None:
            return response(500, {"error": "Answer key unavailable"})

        expected = int(expected)

        return response(200, {
            "qId": qid,
            "correct": given == expected,
            "correctAnswerIndex": expected
        })

    except json.JSONDecodeError:
        return response(400, {"error": "Invalid JSON body"})

    except Exception as error:
        print("Answer check error:", str(error))
        return response(500, {"error": "Internal server error"})
      
# API route: POST /exams/{examId}/answer
# 3. submitExam — Grade and save the exam
# Purpose: Grades the complete submission against the answer keys stored in DynamoDB, calculates the score, and saves the attempt to the Attempts table.

import json
import boto3
import uuid
from datetime import datetime, timezone
from decimal import Decimal

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-southeast-2"
)

exams_table = dynamodb.Table("Exams")
attempts_table = dynamodb.Table("Attempts")


def json_safe(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError(f"Not serializable: {type(obj).__name__}")


def response(status, data):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "content-type",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(data, default=json_safe)
    }


def lambda_handler(event, context):
    try:
        path = event.get("pathParameters") or {}
        exam_id = path.get("examId")

        if not exam_id:
            return response(400, {"error": "Missing examId"})

        raw_body = event.get("body") or "{}"
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

        user_name = body.get("userName")
        submitted_answers = body.get("answers")

        if not isinstance(user_name, str) or not user_name.strip():
            return response(400, {"error": "Missing userName"})

        if not isinstance(submitted_answers, list):
            return response(400, {"error": "Answers must be a list"})

        result = exams_table.get_item(Key={"examId": exam_id})
        exam = result.get("Item")

        if not exam:
            return response(404, {"error": "Exam not found"})

        questions = exam.get("questions", [])

        if not questions:
            return response(400, {"error": "Exam has no questions"})

        answer_map = {}

        for answer in submitted_answers:
            qid = answer.get("qId")

            if not qid or qid in answer_map:
                return response(400, {"error": "Missing or duplicate qId"})

            answer_map[qid] = answer

        results = []
        score = 0

        for question in questions:
            qid = question.get("qId")
            answer = answer_map.get(qid)
            correct = False

            if answer:
                if question.get("type", "mcq") == "short":
                    expected = question.get("correctAnswerText", "")
                    given = answer.get("answerText", "")

                    correct = (
                        isinstance(given, str)
                        and given.strip().casefold()
                        == str(expected).strip().casefold()
                    )
                else:
                    expected = question.get("correctAnswerIndex")
                    given = answer.get("answerIndex")

                    if expected is not None and given is not None:
                        try:
                            correct = (
                                not isinstance(given, bool)
                                and int(given) == int(expected)
                            )
                        except (TypeError, ValueError):
                            correct = False

            if correct:
                score += 1

            results.append({
                "qId": qid,
                "correct": correct
            })

        attempt_id = str(uuid.uuid4())

        attempts_table.put_item(
            Item={
                "attemptId": attempt_id,
                "examId": exam_id,
                "userName": user_name.strip(),
                "score": score,
                "total": len(questions),
                "results": results,
                "submittedAt": datetime.now(timezone.utc).isoformat()
            }
        )

        return response(200, {
            "attemptId": attempt_id,
            "score": score,
            "total": len(questions),
            "results": results
        })

    except json.JSONDecodeError:
        return response(400, {"error": "Invalid JSON body"})

    except Exception as error:
        print("submitExam error:", str(error))
        return response(500, {"error": "Internal server error"})
      
# API route: POST /exams/{examId}/submit

