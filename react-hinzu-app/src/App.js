import React from "react";

import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";

// import "./App.css";
// import "bootstrap/dist/css/bootstrap.min.css";

import FileUpload from "./views/UploadView/UploadView";
// import ResultView from "./views/ResultView/ResultView";
import { ThemeProvider, createMuiTheme } from '@material-ui/core/styles';

// to change font style for all element we should provide theme
// now it is defualt
const THEME = createMuiTheme({
   typography: {
    "fontFamily": `"Girlous", "Roboto", "Helvetica", "Arial", sans-serif`,
    "fontSize": 14,
    "fontWeightLight": 300,
    "fontWeightRegular": 400,
    "fontWeightMedium": 500
   }
});

function App() {
  return (
    <ThemeProvider theme={THEME}>
    <Router>
      <Switch>
        {/* <Route path="/result">
            <ResultView />
        </Route> */}
        <Route path="/">
          {/* <div className="container" style={{ width: "600px" }}> */}
          <FileUpload />
          {/* </div> */}
        </Route>

      </Switch>
    </Router>
  </ThemeProvider>


  );
}

export default App;
