function Header({ page, setPage }) {
  return (
    <header className="header">
      <div className="logo">CryptoMix</div>

      <nav className="nav">
        <button
          className={page === "home" ? "nav-link active" : "nav-link"}
          onClick={() => setPage("home")}
        >
          Home
        </button>

        <button
          className={page === "cipher" ? "nav-link active" : "nav-link"}
          onClick={() => setPage("cipher")}
        >
          Cipher
        </button>
      </nav>
    </header>
  );
}

export default Header;
