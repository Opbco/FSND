# The Great Bookshelf of Udacity

This project is trivia where people can register questions by categories and thier answer and play a quizz game. As a part of the Fullstack Nanodegree, it serves as a practice module for lessons from Course 2: API Development and Documentation. By completing this project, I learned and apply my skills structuring and implementing well formatted API endpoints that leverage knowledge of HTTP and API development best practices.

All backend code follows [PEP8 style guidelines](https://www.python.org/dev/peps/pep-0008/).

## Getting Started

### Pre-requisites and Local Development

Developers using this project should already have Python3, pip and node installed on their local machines.

#### Backend

From the backend folder run `pip install requirements.txt`. All required packages are included in the requirements file.

### Database Setup

With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:

```bash
psql trivia < trivia.psql
```

### Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

These commands put the application in development and directs our application to use the `__init__.py` file in our flaskr folder. Working in development mode shows an interactive debugger in the console and restarts the server whenever changes are made. If running locally on Windows, look for the commands in the [Flask documentation](http://flask.pocoo.org/docs/1.0/tutorial/factory/).

The application is run on `http://127.0.0.1:5000/` by default and is a proxy in the frontend configuration.

## Testing

To run the tests, run

```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

#### Frontend

From the frontend folder, run the following commands to start the client:

```
npm install // only once to install dependencies
npm start
```

By default, the frontend will run on localhost:3000.

The first time you run the tests, omit the dropdb command.

All tests are kept in that file and should be maintained as updates are made to app functionality.

## API Reference

### Getting Started

- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/api/v1.0/`, which is set as a proxy in the frontend configuration.
- Authentication: This version of the application does not require authentication or API keys.

### Error Handling

Errors are returned as JSON objects in the following format:

```
{
    "success": False,
    "error": 400,
    "message": "Bad request"
}
```

The API will return three error types when requests fail:

- 400: Bad request
- 404: Resource not found
- 405: Method Not Allowed
- 422: Unprocessable Entity
- 500: Internal Server Error

### Endpoints

#### GET /categories

- General:
  - Returns a list of categories objects, success value, and total number of categories.
- Sample: `curl http://127.0.0.1:5000/api/v1.0/categories`

```{
  "categories": [
    {
      "id": 2,
      "type": "Art"
    },
    {
      "id": 5,
      "type": "Entertainment"
    },
    {
      "id": 3,
      "type": "Geography"
    },
    {
      "id": 4,
      "type": "History"
    },
    {
      "id": 1,
      "type": "Sciences"
    },
    {
      "id": 6,
      "type": "Sports"
    }
  ],
  "success": true,
  "total_categories": 6
}
```

#### GET /questions

- General:
  - Returns a list of questions objects, success value, and total number of questions, current category's type, list of categories objects.
  - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1.
- Sample: `curl http://127.0.0.1:5000/api/v1.0/questions?page=1`

```{
  "categories": [
    {
      "id": 2,
      "type": "Art"
    },
    {
      "id": 5,
      "type": "Entertainment"
    },
    {
      "id": 3,
      "type": "Geography"
    },
    {
      "id": 4,
      "type": "History"
    },
    {
      "id": 1,
      "type": "Sciences"
    },
    {
      "id": 6,
      "type": "Sports"
    }
  ],
  "category": "Geography",
  "questions": [
    {
      "answer": "Lake Victoria",
      "category": "Geography",
      "difficulty": 2,
      "id": 10,
      "question": "What is the largest lake in Africa?"
    },
    {
      "answer": "George Washington Carver",
      "category": "History",
      "difficulty": 2,
      "id": 9,
      "question": "Who invented Peanut Butter?"
    },
    {
      "answer": "Uruguay",
      "category": "Sports",
      "difficulty": 4,
      "id": 7,
      "question": "Which country won the first ever soccer World Cup in 1930?"
    },
    {
      "answer": "Brazil",
      "category": "Sports",
      "difficulty": 3,
      "id": 6,
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": "Entertainment",
      "difficulty": 3,
      "id": 5,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    },
    {
      "answer": "Tom Cruise",
      "category": "Entertainment",
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
    {
      "answer": "Muhammad Ali",
      "category": "History",
      "difficulty": 2,
      "id": 2,
      "question": "What boxer's original name is Cassius Clay?"
    }
  ],
  "success": true,
  "total_questions": 17
}
```

#### GET /categories/{category_id}/questions

- General:
  - Returns a list of questions objects, success value, and total number of questions for the current category, current category object.
  - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1.
- Sample: `curl http://127.0.0.1:5000/api/v1.0/categories/3/questions?page=1`

```{
  "category": {
    "id": 3,
    "type": "Geography"
  },
  "questions": [
    {
      "answer": "Lake Victoria",
      "category": "Geography",
      "difficulty": 2,
      "id": 10,
      "question": "What is the largest lake in Africa?"
    },
    {
      "answer": "The Palace of Versailles",
      "category": "Geography",
      "difficulty": 3,
      "id": 11,
      "question": "In which royal palace would you find the Hall of Mirrors?"
    },
    {
      "answer": "Agra",
      "category": "Geography",
      "difficulty": 2,
      "id": 12,
      "question": "The Taj Mahal is located in which Indian city?"
    }
  ],
  "success": true,
  "total_questions": 3
}
```

#### POST /questions

- General:
  - Creates new question using the submitted question, answer, difficulty and category. Returns the created question object, success value.
- `curl http://127.0.0.1:5000/api/v1.0/questions -X POST -H "Content-Type: application/json" -d '{"question": "who did this project?", "answer": "Owono Philippe Brice", "difficulty": 2, "category": 1}'`

```
{
  "question": {
    "answer": "Owono Philippe Brice",
    "category": "Sciences",
    "difficulty": 2,
    "id": 23,
    "question": "who did this project?"
  },
  "success": true
}
```

#### DELETE /questions/{question_id}

- General:
  - Deletes the question of the given ID if it exists. Returns the id of the deleted question, success value and the message "question deleted successfully".
- `curl -X DELETE http://127.0.0.1:5000/api/v1.0/questions/23`

```
{
  "message": "question deleted successfully",
  "question_id": 23,
  "success": true
}
```

#### POST /questions

- General:
  - If provided, search for all questions that contains the searchTerm, then return a lis of questions objects, the search term, success value and total of questions.
- `curl http://127.0.0.1:5000/api/v1.0/questions -X POST -H "Content-Type: application/json" -d '{"searchTerm":"title"}'`

```
{
  "questions": [
    {
      "answer": "Maya Angelou",
      "category": "History",
      "difficulty": 2,
      "id": 22,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": "Entertainment",
      "difficulty": 3,
      "id": 5,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }
  ],
  "searchTerm": "title",
  "success": true,
  "total_questions": 2
}
```

#### POST /quizzes

- General:
  - Returns a question object and success value.
  - Get the previous questions and a selected category
- Sample: `curl http://localhost:5000/api/v1.0/quizzes -X POST -H "Content-Type:application/json" -d '{"quiz_category":{"id":3, "type":"Art"}, "previous_questions":[1,3,4]}'`

```{
  "question": {
    "answer": "The Palace of Versailles",
    "category": "Geography",
    "difficulty": 3,
    "id": 11,
    "question": "In which royal palace would you find the Hall of Mirrors?"
  },
  "success": true
}
```

## Deployment N/A

## Authors

Yours truly, Student Owono Philippe Brice

## Acknowledgements

The awesome team at Udacity, soon to be full stack extraordinaires!
