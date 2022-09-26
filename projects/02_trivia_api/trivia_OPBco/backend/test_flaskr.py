import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:OPBco@{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "who did this project, submited and then resubmited?",
                             "answer": "Owono Philippe Brice", "difficulty": 2, "category": 1}

        self.error_question = {"question": "who did this project again?",
                               "answer": "Owono Philippe Brice", "difficulty": "sde", "category": 1}

        self.quizz_question = {"previous_questions": [
            1, 3, 4], "quiz_category": {"id": 1, "type": "Sciences"}}

        self.quizz_question400 = {"previous_questions": [
            1, 3, 4], "quiz_categories": {"id": 1, "type": "Sciences"}}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            # self.db.create_all()

        self.last_question = Question.query.order_by(
            self.db.desc(Question.id)).first()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # test the endpoint to get all the categories

    def test_get_all_categories(self):
        res = self.client().get("/api/v1.0/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_categories"])
        self.assertTrue(len(data["categories"]))

    def test_405_if_category_creation_not_allowed(self):
        res = self.client().post("/api/v1.0/categories",
                                 json={"type": "Astrology"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method Not Allowed")

    # test the endpoint to get the paginated list of questions
    def test_get_paginated_questions(self):
        res = self.client().get("/api/v1.0/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(len(data["questions"]))

    def test_get_paginated_questions_beyond_valid_page(self):
        res = self.client().get("/api/v1.0/questions?page=100")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # test the endpoint to get questions of a particular category
    def test_get_paginated_questions_per_category(self):
        res = self.client().get("/api/v1.0/categories/3/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["category"])
        self.assertTrue(len(data["questions"]))

    def test_get_paginated_questions_for_non_existing_category(self):
        res = self.client().get("/api/v1.0/categories/3000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # test the endpoint to get the list of questions that match the search term
    def test_search_questions(self):
        res = self.client().post("/api/v1.0/questions",
                                 json={"searchTerm": "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 2)
        self.assertEqual(data["searchTerm"], "title")
        self.assertTrue(len(data["questions"]))

    def test_search_question_with_non_matching_term(self):
        res = self.client().post("/api/v1.0/questions",
                                 json={"searchTerm": "OPBco"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # test the Endpoint to delete a question knowing its id
    def test_delete_book(self):
        res = self.client().delete("/api/v1.0/questions/{}".format(self.last_question.id))
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.id == self.last_question.id).one_or_none()

        print(question)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["question_id"], self.last_question.id)
        self.assertEqual(data["message"], "question deleted successfully")
        self.assertEqual(question, None)

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # test the endpoint to add a question to the database
    def test_save_questions(self):
        res = self.client().post("/api/v1.0/questions",
                                 json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_422_on_save_questions(self):
        res = self.client().post("/api/v1.0/questions",
                                 json=self.error_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable Entity")

    def test_405_on_save_questions(self):
        res = self.client().put("/api/v1.0/questions",
                                json=self.error_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method Not Allowed")

    # test the endpoints to get a random question
    def test_get_quizz_question(self):
        res = self.client().post("/api/v1.0/quizzes",
                                 json=self.quizz_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_get_quizz_question_error_400(self):
        res = self.client().post("/api/v1.0/quizzes",
                                 json=self.quizz_question400)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
