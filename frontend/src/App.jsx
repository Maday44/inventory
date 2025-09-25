
/*
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./HomePage";
import ProfilePage from "./ProfilePage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
    </Router>
  );
}
*/
//export default App;




import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./home";
import AllFoodPage from "./AllFoodPage";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/food" element={<AllFoodPage />} />
      </Routes>
    </Router>
  );
}

export default App;
