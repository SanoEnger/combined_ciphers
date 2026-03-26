function Home({ setPage }) {
  return (
    <div>
      <section className="hero">
        <div className="hero-text">
          <h1>Комбинированное шифрование</h1>
          <p>
            Сайт для работы с <strong>шифром замены</strong>,
            <strong> шифром перестановки</strong> и их
            <strong> последовательным комбинированием</strong>.
          </p>

          <button className="btn" onClick={() => setPage("cipher")}>
            Перейти к шифрованию
          </button>
        </div>

        <div className="hero-card">
          <div className="card-glow"></div>
          <h3>Доступные режимы</h3>
          <ul>
            <li>Только шифр замены</li>
            <li>Только шифр перестановки</li>
            <li>Замена + перестановка</li>
            <li>Перестановка + замена</li>
          </ul>
        </div>
      </section>

      <section className="info-grid">
        <article className="info-card">
          <h2>Шифр замены</h2>
          <p>
            Метод, при котором каждый символ исходного текста заменяется другим
            символом по определённому правилу. В этом проекте используется сдвиг
            по алфавиту.
          </p>
        </article>

        <article className="info-card">
          <h2>Шифр перестановки</h2>
          <p>
            Метод, при котором символы не заменяются, а меняют своё расположение
            по определённому ключу. Это помогает скрыть структуру исходного
            сообщения.
          </p>
        </article>

        <article className="info-card">
          <h2>Комбинированный подход</h2>
          <p>
            Для повышения стойкости можно сначала применить шифр замены, а затем
            выполнить перестановку символов. Такой способ делает анализ
            шифртекста более сложным.
          </p>
        </article>
      </section>
    </div>
  );
}

export default Home;
