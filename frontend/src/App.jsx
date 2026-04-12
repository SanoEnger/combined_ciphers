import Home from "./pages/home";
import Cipher from "./pages/cipher";
import Header from "./components/Header";
import { useState } from "react";

function App() {
  const [page, setPage] = useState("home");

  return (
    <div>
      <Header page={page} setPage={setPage} />
      {page === "home" ? <Home setPage={setPage} /> : <Cipher />}
    </div>
  );
}

export default App;
