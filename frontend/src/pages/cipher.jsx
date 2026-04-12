import { useMemo, useState } from "react";
import { processCipher } from "../api";

const modeOptions = [
  { value: "substitution", label: "Только шифр замены" },
  { value: "transposition", label: "Только шифр перестановки" },
  { value: "combined_sp", label: "Комбинированный (замена + перестановка)" },
  { value: "combined_ps", label: "Комбинированный (перестановка + замена)" },
];

const actionOptions = [
  { value: "encrypt", label: "Зашифровать" },
  { value: "decrypt", label: "Расшифровать" },
];

const orderOptions = [
  { value: "row", label: "По строкам (слева направо)" },
  { value: "snake_left_right", label: "Змейкой (← →)" },
  { value: "snake_right_left", label: "Змейкой с верхнего правого угла (→ ←)" },
  { value: "snake_top_down", label: "Змейкой по столбцам (↓ ↑)" },
  { value: "snake_bottom_up", label: "Змейкой по столбцам снизу вверх" },
];

const RUS_ALPHABET = [
  "А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И", "Й", "К", "Л", "М",
  "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Ъ", "Ы", "Ь", "Э", "Ю", "Я",
];

function Cipher() {
  const [mode, setMode] = useState("substitution");
  const [action, setAction] = useState("encrypt");
  const [slogan, setSlogan] = useState("ЛОПАТА");
  const [period, setPeriod] = useState(8);
  const [order, setOrder] = useState("row");
  const [inputText, setInputText] = useState("нетакиеметеливлицолетели");
  const [matrixRows, setMatrixRows] = useState(3);
  const [matrixCols, setMatrixCols] = useState(5);
  
  const [resultSteps, setResultSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const buttonState = useMemo(() => {
    return {
      canGoPrev: currentStep > 0,
      canGoNext: currentStep < resultSteps.length - 1,
      hasSteps: resultSteps.length > 0,
    };
  }, [currentStep, resultSteps]);

  const processText = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Очищаем текст при расшифровании
      let cleanedText = inputText;
      if (action === "decrypt") {
        cleanedText = inputText.toUpperCase().replace(/[^А-ЯЁ]/g, '');
        if (!cleanedText) {
          throw new Error("Текст не содержит букв русского алфавита");
        }
      }
      
      let requestBody = {
        mode: mode === "combined_sp" ? "sub_then_trans" : 
              mode === "combined_ps" ? "trans_then_sub" : mode,
        operation: action,
        text: cleanedText,
        read_method: order,
      };
      
      if (mode === "substitution" || mode === "combined_sp" || mode === "combined_ps") {
        requestBody.sub_key = slogan;
        requestBody.period = period;
      }
      
      const needsMatrix = (mode === "transposition" || mode === "combined_sp" || mode === "combined_ps");
      if (needsMatrix && action === "decrypt") {
        if (!matrixRows || !matrixCols) {
          throw new Error("Для расшифрования укажите количество строк и столбцов матрицы");
        }
        requestBody.m = matrixRows;
        requestBody.n = matrixCols;
      }
      
      console.log("Sending request:", requestBody);
      const response = await processCipher(requestBody);
      console.log("Response:", response);
      
      const formattedSteps = response.steps.map((step) => ({
        stage: step.step,
        title: step.title,
        description: step.description,
        source_text: step.source_text,
        result_text: step.result_text,
        visualization: step.visualization,
      }));
      
      setResultSteps(formattedSteps);
      setCurrentStep(0);
    } catch (err) {
      console.error("Error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const prevStep = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  };

  const nextStep = () => {
    setCurrentStep((prev) => Math.min(prev + 1, resultSteps.length - 1));
  };

  const nextStage = () => {
    if (!resultSteps[currentStep]) return;
    const nextIndex = resultSteps.findIndex(
      (step, index) => index > currentStep && step.stage !== resultSteps[currentStep].stage,
    );
    if (nextIndex !== -1) setCurrentStep(nextIndex);
  };

  const resetStage = () => {
    if (!resultSteps[currentStep]) return;
    const firstIndexOfCurrentStage = resultSteps.findIndex(
      (step) => step.stage === resultSteps[currentStep].stage,
    );
    if (firstIndexOfCurrentStage !== -1) setCurrentStep(firstIndexOfCurrentStage);
  };

  const resetAll = () => {
    setCurrentStep(0);
  };

  const renderCurrentStep = () => {
    if (resultSteps.length === 0) {
      return (
        <div className="empty-result">
          {error ? <div style={{ color: "red" }}>Ошибка: {error}</div> : "Здесь появится результат выполнения."}
        </div>
      );
    }

    const step = resultSteps[currentStep];
    if (!step) return <div>Шаг не найден</div>;

    // Визуализация матрицы перестановки
    if (step.visualization && step.visualization.matrix) {
      return (
        <div className="step-view">
          <h3 className="step-title">{step.title}</h3>
          {step.visualization.read_description && (
            <div className="matrix-read-method">
              <small>Метод чтения: {step.visualization.read_description}</small>
            </div>
          )}
          <div className="table-wrap">
            <table className="matrix-table clean-light-table">
              <tbody>
                {step.visualization.matrix.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {row.map((cell, colIndex) => (
                      <td key={colIndex}>{cell || ""}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }

    // Визуализация таблицы алфавитов замены
    if (step.visualization && step.visualization.type === "substitution" && step.visualization.rows) {
      return (
        <div className="step-view">
          <h3 className="step-title">{step.title}</h3>
          {step.visualization.keyword && (
            <div className="alphabet-info">
              <small>Лозунг: {step.visualization.keyword} | Период: {step.visualization.period}</small>
            </div>
          )}
          <div className="table-wrap">
            <table className="alphabet-table clean-light-table">
              <tbody>
                <tr>
                  <th>№</th>
                  {step.visualization.base_alphabet?.map((letter, index) => (
                    <th key={index}>{letter}</th>
                  ))}
                </tr>
                {step.visualization.rows.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    <td>{row.position_in_period || rowIndex + 1}</td>
                    {row.shifted_alphabet.map((letter, colIndex) => (
                      <td key={colIndex}>{letter}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }

    // Визуализация привязки позиций к номерам алфавитов (шаг 3) в виде таблицы
    if (step.visualization && step.visualization.type === "position_mapping" && step.visualization.positions) {
      const positions = step.visualization.positions;
      return (
        <div className="step-view">
          <h3 className="step-title">{step.title}</h3>
          {step.description && <p style={{ color: "#666", fontSize: "14px", marginBottom: "15px" }}>{step.description}</p>}
          <div className="table-wrap">
            <table className="alphabet-table clean-light-table">
              <tbody>
                <tr>
                  <th>№ алфавита</th>
                  {positions.map((pos, idx) => (
                    <td key={idx}>{pos.alphabet_number}</td>
                  ))}
                </tr>
                <tr>
                  <th>Буква</th>
                  {positions.map((pos, idx) => (
                    <td key={idx}>{pos.char}</td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
          {step.source_text && (
            <div className="summary-item" style={{ marginTop: "15px" }}>
              <span className="summary-label">Текст:</span>
              <span>{step.source_text}</span>
            </div>
          )}
        </div>
      );
    }

    // Обычный шаг с текстом
    return (
      <div className="step-view">
        <h3 className="step-title">{step.title}</h3>
        {step.description && <p style={{ color: "#666", fontSize: "14px", marginBottom: "15px" }}>{step.description}</p>}
        <div className="summary-list">
          {step.source_text && (
            <div className="summary-item">
              <span className="summary-label">Текст:</span>
              <span>{step.source_text}</span>
            </div>
          )}
          {step.result_text && step.result_text !== step.source_text && (
            <div className="summary-item summary-item-result">
              <span className="summary-label">Результат:</span>
              <span>{step.result_text}</span>
            </div>
          )}
          {step.result_text && !step.source_text && (
            <div className="summary-item">
              <span className="summary-label">Результат:</span>
              <span>{step.result_text}</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="page-content">
      <section className="page-title">
        <h1>Шифрование и расшифровка</h1>
        <p>Выберите режим и введите параметры шифрования.</p>
      </section>

      <section className="cipher-layout">
        <div className="panel">
          <label htmlFor="mode">Режим</label>
          <select id="mode" value={mode} onChange={(e) => setMode(e.target.value)}>
            {modeOptions.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>

          <label htmlFor="action">Действие</label>
          <select id="action" value={action} onChange={(e) => setAction(e.target.value)}>
            {actionOptions.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>

          {mode === "substitution" && (
            <>
              <label htmlFor="slogan">Лозунг (слово для построения алфавита)</label>
              <textarea
                id="slogan"
                rows="2"
                value={slogan}
                onChange={(e) => setSlogan(e.target.value)}
                placeholder="Введите слово-лозунг (например: ЛОПАТА)"
              />

              <label htmlFor="period">Период (количество алфавитов)</label>
              <input
                type="number"
                id="period"
                value={period}
                min="1"
                max="33"
                onChange={(e) => setPeriod(Number(e.target.value))}
              />
              <small style={{ marginTop: "-10px", marginBottom: "10px", display: "block", color: "#666" }}>
                Количество различных алфавитов замены (от 1 до 33)
              </small>

              <label htmlFor="sourceText">Исходный текст</label>
              <textarea
                id="sourceText"
                rows="7"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />
            </>
          )}

          {mode === "transposition" && (
            <>
              {action === "decrypt" && (
                <>
                  <label htmlFor="matrixRows">Число строк (m)</label>
                  <input
                    type="number"
                    id="matrixRows"
                    value={matrixRows}
                    min="1"
                    max="10"
                    onChange={(e) => setMatrixRows(Number(e.target.value))}
                  />

                  <label htmlFor="matrixCols">Число столбцов (n)</label>
                  <input
                    type="number"
                    id="matrixCols"
                    value={matrixCols}
                    min="1"
                    max="10"
                    onChange={(e) => setMatrixCols(Number(e.target.value))}
                  />
                </>
              )}

              <label htmlFor="order">Порядок чтения матрицы</label>
              <select id="order" value={order} onChange={(e) => setOrder(e.target.value)}>
                {orderOptions.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>

              <label htmlFor="sourceText">Исходный текст</label>
              <textarea
                id="sourceText"
                rows="7"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />
            </>
          )}

          {(mode === "combined_sp" || mode === "combined_ps") && (
            <>
              <h3 className="section-mini-title">
                {mode === "combined_sp" ? "Сначала: шифр замены" : "Сначала: шифр перестановки"}
              </h3>

              <label htmlFor="slogan">Лозунг (слово для построения алфавита)</label>
              <textarea
                id="slogan"
                rows="2"
                value={slogan}
                onChange={(e) => setSlogan(e.target.value)}
                placeholder="Введите слово-лозунг (например: ЛОПАТА)"
              />

              <label htmlFor="period">Период (количество алфавитов)</label>
              <input
                type="number"
                id="period"
                value={period}
                min="1"
                max="33"
                onChange={(e) => setPeriod(Number(e.target.value))}
              />
              <small style={{ marginTop: "-10px", marginBottom: "15px", display: "block", color: "#666" }}>
                Количество различных алфавитов замены
              </small>

              <h3 className="section-mini-title">
                {mode === "combined_sp" ? "Потом: шифр перестановки" : "Потом: шифр замены"}
              </h3>

              {action === "decrypt" && (
                <>
                  <label htmlFor="matrixRows">Число строк (m)</label>
                  <input
                    type="number"
                    id="matrixRows"
                    value={matrixRows}
                    min="1"
                    max="10"
                    onChange={(e) => setMatrixRows(Number(e.target.value))}
                  />

                  <label htmlFor="matrixCols">Число столбцов (n)</label>
                  <input
                    type="number"
                    id="matrixCols"
                    value={matrixCols}
                    min="1"
                    max="10"
                    onChange={(e) => setMatrixCols(Number(e.target.value))}
                  />
                </>
              )}

              <label htmlFor="order">Порядок чтения матрицы</label>
              <select id="order" value={order} onChange={(e) => setOrder(e.target.value)}>
                {orderOptions.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>

              <label htmlFor="sourceText">Исходный текст</label>
              <textarea
                id="sourceText"
                rows="7"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />
            </>
          )}

          <button className="btn full" onClick={processText} disabled={loading}>
            {loading ? "Обработка..." : "Выполнить"}
          </button>
        </div>

        <div className="panel result-panel">
          <div className="result-header">
            <h2>Результат</h2>
            {buttonState.hasSteps && (
              <div className="step-badge">
                Шаг {currentStep + 1} / {resultSteps.length}
              </div>
            )}
          </div>

          <div className="result-box">{renderCurrentStep()}</div>

          <div className="step-controls">
            <button className="btn small-btn" onClick={prevStep} disabled={!buttonState.canGoPrev}>
              Предыдущий шаг
            </button>

            <button className="btn small-btn" onClick={nextStep} disabled={!buttonState.canGoNext}>
              Следующий шаг
            </button>

            <button className="btn small-btn" onClick={nextStage} disabled={!buttonState.hasSteps}>
              К следующему этапу
            </button>

            <button className="btn small-btn" onClick={resetStage} disabled={!buttonState.hasSteps}>
              В начало этапа
            </button>

            <button className="btn small-btn" onClick={resetAll} disabled={!buttonState.hasSteps}>
              В самое начало
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Cipher;