import React, { Component } from "react";
import logo from "../logo.svg";
import "../stylesheets/Header.css";

class Header extends Component {
  navTo(uri) {
    window.location.href = window.location.origin + uri;
  }

  render() {
    return (
      <div className="App-header">
        <h1
          className="btn"
          onClick={() => {
            this.navTo("");
          }}
        >
          Udacitrivia
        </h1>
        <h2
          className="btn"
          onClick={() => {
            this.navTo("");
          }}
        >
          List
        </h2>
        <h2
          className="btn"
          onClick={() => {
            this.navTo("/add");
          }}
        >
          Add
        </h2>
        <h2
          className="btn"
          onClick={() => {
            this.navTo("/play");
          }}
        >
          Play
        </h2>
      </div>
    );
  }
}

export default Header;
