from operator import and_
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import random

from models import setup_db, db, Question, Category

QUESTIONS_PER_PAGE = 10


def handle_pagination(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    return selection[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    migrate = Migrate(app, db)
    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/api/v1.0/categories')
    def get_categories():
        current_categories = [
            category.format() for category in Category.query.order_by(Category.type).all()]
        return jsonify({"success": True, "categories": current_categories, "total_categories": len(current_categories)})

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/api/v1.0/questions')
    def get_questions():
        allFormattedQuestions = [question.format()
                                 for question in Question.query.order_by(db.desc(Question.id)).all()]
        if len(allFormattedQuestions) == 0:
            abort(404)
        else:
            paginate_questions = handle_pagination(
                request, allFormattedQuestions)

            if len(paginate_questions) == 0:
                abort(404)
            else:
                allcategories = [
                    category.format() for category in Category.query.order_by(Category.type).all()]
                return jsonify({
                    "questions": paginate_questions,
                    "total_questions": len(allFormattedQuestions),
                    "category": paginate_questions[0]["category"],
                    "categories": allcategories,
                    "success": True
                })

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/api/v1.0/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        if question is None:
            abort(404)
        else:
            try:
                question.delete()
                return jsonify({
                    'success': True,
                    'question_id': question_id,
                    'message': 'question deleted successfully'
                })
            except:
                abort(422)
    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    '''        
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route('/api/v1.0/questions', methods=['POST'])
    def get_search_questions():
        data = request.get_json()
        question = data.get('question', None)
        answer = data.get('answer', None)
        difficulty = data.get('difficulty', 0)
        category = data.get('category', 0)
        if 'searchTerm' in data:
            queryQuestions = Question.query.filter(Question.question.ilike(
                '%'+data['searchTerm']+'%')).order_by(Question.category_id).all()
            allFormattedQuestions = [question.format()
                                     for question in queryQuestions]
            if len(allFormattedQuestions) == 0:
                abort(404)
            else:
                return jsonify({
                    "questions": allFormattedQuestions,
                    "total_questions": len(allFormattedQuestions),
                    "searchTerm": data['searchTerm'],
                    "success": True
                })
        else:
            if question is None or answer is None or category is None or difficulty == 0:
                abort(400)
            else:
                try:
                    question_new = Question(question=question, answer=answer, category_id=int(
                        category), difficulty=int(difficulty))
                    question_new.insert()
                    return jsonify({
                        'success': True,
                        'question': question_new.format()
                    })
                except:
                    abort(422)
    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/api/v1.0/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        current_category = Category.query.filter(
            Category.id == category_id).one_or_none()

        if current_category is None:
            abort(404)
        else:
            allFormattedQuestions = [question.format()
                                     for question in current_category.questions]
            if len(allFormattedQuestions) == 0:
                abort(404)
            else:
                paginate_questions = handle_pagination(
                    request, allFormattedQuestions)
                if len(paginate_questions) == 0:
                    abort(404)
                else:
                    return jsonify({
                        "questions": paginate_questions,
                        "total_questions": len(allFormattedQuestions),
                        "category": current_category.format(),
                        "success": True
                    })

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/api/v1.0/quizzes', methods=['POST'])
    def get_quizz_question():
        data = request.get_json()
        if 'previous_questions' in data and 'quiz_category' in data:
            if data['quiz_category']['id']:
                questionsAvailable = db.session.query(Question).join(Category, and_(
                    Question.category_id == Category.id, Category.id == data['quiz_category']['id'])).filter(
                    ~Question.id.in_(data['previous_questions'])).all()
            else:
                questionsAvailable = db.session.query(Question).join(
                    Category, Question.category_id == Category.id).filter(~Question.id.in_(data['previous_questions'])).all()
            if len(questionsAvailable) == 0:
                return jsonify({
                    "question": None,
                    "success": True
                })
            else:
                formatedQuestions = [question.format()
                                     for question in questionsAvailable]
                question = random.choice(formatedQuestions)

                return jsonify({
                    "question": question,
                    "success": True
                })
        else:
            abort(400)
    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app
