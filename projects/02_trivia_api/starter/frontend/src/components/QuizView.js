import React, { Component } from "react";
import $ from "jquery";

import "../stylesheets/QuizView.css";

const questionsPerPlay = 5;

class QuizView extends Component {
  constructor(props) {
    super(props);
    this.state = {
      quizCategory: null,
      previousQuestions: [],
      showAnswer: false,
      categories: [],
      numCorrect: 0,
      currentQuestion: {},
      guess: "",
      forceEnd: false,
    };
  }

  componentDidMount() {
    $.ajax({
      url: `http://127.0.0.1:5000/api/v1.0/categories`, //TODO: update request URL
      type: "GET",
      success: (result) => {
        this.setState({ categories: result.categories });
      },
      error: (error) => {
        alert("Unable to load categories. Please try your request again");
      },
    });
  }

  selectCategory = ({ type, id = 0 }) => {
    this.setState({ quizCategory: { type, id } }, this.getNextQuestion);
  };

  handleChange = (event) => {
    this.setState({ [event.target.name]: event.target.value });
  };

  getNextQuestion = () => {
    const previousQuestions = [...this.state.previousQuestions];
    if (this.state.currentQuestion.id) {
      previousQuestions.push(this.state.currentQuestion.id);
    }

    $.ajax({
      url: `http://127.0.0.1:5000/api/v1.0/quizzes`, //TODO: update request URL
      type: "POST",
      dataType: "json",
      contentType: "application/json",
      data: JSON.stringify({
        previous_questions: previousQuestions,
        quiz_category: this.state.quizCategory,
      }),
      xhrFields: {
        withCredentials: true,
      },
      crossDomain: true,
      success: (result) => {
        this.setState({
          showAnswer: false,
          previousQuestions: previousQuestions,
          currentQuestion: result.question,
          guess: "",
          forceEnd: result.question ? false : true,
        });
      },
      error: (error) => {
        alert("Unable to load question. Please try your request again");
      },
    });
  };

  submitGuess = (event) => {
    event.preventDefault();
    const formatGuess = this.state.guess
      .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, "")
      .toLowerCase();
    const evaluate = this.evaluateAnswer();
    this.setState({
      numCorrect: !evaluate ? this.state.numCorrect : this.state.numCorrect + 1,
      showAnswer: true,
    });
  };

  restartGame = () => {
    this.setState({
      quizCategory: null,
      previousQuestions: [],
      showAnswer: false,
      numCorrect: 0,
      currentQuestion: {},
      guess: "",
      forceEnd: false,
    });
  };

  renderPrePlay() {
    return (
      <div className="quiz-play-holder">
        <div className="choose-header">Choose Category</div>
        <div className="category-holder">
          <div className="play-category btn" onClick={this.selectCategory}>
            ALL
          </div>
          {this.state.categories.map((category, index) => {
            return (
              <div
                key={index}
                value={category.id}
                className="play-category btn"
                onClick={() =>
                  this.selectCategory({ type: category.type, id: category.id })
                }
              >
                {category.type}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  renderFinalScore() {
    return (
      <div className="quiz-play-holder">
        <div className="final-header">
          {" "}
          Your Final Score is {this.state.numCorrect}
        </div>
        <div className="play-again button btn" onClick={this.restartGame}>
          {" "}
          Play Again?{" "}
        </div>
      </div>
    );
  }

  evaluateAnswer = () => {
    const formatGuess = this.state.guess
      .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, "")
      .toLowerCase();
    const answerArray = this.state.currentQuestion.answer
      .toLowerCase()
      .split(" ");
    return answerArray.every((el) => formatGuess.includes(el));
  };

  renderCorrectAnswer() {
    const formatGuess = this.state.guess
      .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, "")
      .toLowerCase();
    const evaluate = this.evaluateAnswer();
    return (
      <div className="quiz-play-holder">
        <div className="quiz-question">
          {this.state.currentQuestion.question}
        </div>
        <div className={`${evaluate ? "correct" : "wrong"}`}>
          {evaluate ? "You were correct!" : "You were incorrect"}
        </div>
        <div className="quiz-answer">{this.state.currentQuestion.answer}</div>
        <div className="next-question button" onClick={this.getNextQuestion}>
          {" "}
          Next Question{" "}
        </div>
      </div>
    );
  }

  renderPlay() {
    return this.state.previousQuestions.length === questionsPerPlay ||
      this.state.forceEnd ? (
      this.renderFinalScore()
    ) : this.state.showAnswer ? (
      this.renderCorrectAnswer()
    ) : (
      <div className="quiz-play-holder">
        <div className="quiz-question">
          {this.state.currentQuestion.question}
        </div>
        <form onSubmit={this.submitGuess}>
          <input type="text" name="guess" onChange={this.handleChange} />
          <input
            className="submit-guess button"
            type="submit"
            value="Submit Answer"
          />
        </form>
      </div>
    );
  }

  render() {
    return this.state.quizCategory ? this.renderPlay() : this.renderPrePlay();
  }
}

export default QuizView;
