import { useMemo, useState } from "react";

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
  { value: "snake_top_right", label: "Змейкой с верхнего правого угла" },
  { value: "row", label: "По строкам" },
  { value: "column", label: "По столбцам" },
];

const RUS_ALPHABET = [
  "А",
  "Б",
  "В",
  "Г",
  "Д",
  "Е",
  "Ё",
  "Ж",
  "З",
  "И",
  "Й",
  "К",
  "Л",
  "М",
  "Н",
  "О",
  "П",
  "Р",
  "С",
  "Т",
  "У",
  "Ф",
  "Х",
  "Ц",
  "Ч",
  "Ш",
  "Щ",
  "Ъ",
  "Ы",
  "Ь",
  "Э",
  "Ю",
  "Я",
];

function getBaseSloganAlphabet() {
  return [
    "Л",
    "О",
    "П",
    "А",
    "Т",
    "Б",
    "В",
    "Г",
    "Д",
    "Е",
    "Ё",
    "Ж",
    "З",
    "И",
    "Й",
    "К",
    "М",
    "Н",
    "Р",
    "С",
    "У",
    "Ф",
    "Х",
    "Ц",
    "Ч",
    "Ш",
    "Щ",
    "Ъ",
    "Ы",
    "Ь",
    "Э",
    "Ю",
    "Я",
  ];
}

function getShiftedAlphabets(shift = 8) {
  const base = getBaseSloganAlphabet();

  return Array.from({ length: shift }, (_, rowIndex) => {
    return [...base.slice(rowIndex), ...base.slice(0, rowIndex)];
  });
}

function getTranspositionMockSteps() {
  const matrix = [
    ["", "е", "ь", "е", ""],
    ["а", "а", "т", "о", "с"],
    ["з", "о", "к", "б", "р"],
    ["а", "р", "с", "о", "о"],
    ["т", "о", "с", "у", "к"],
    ["е", "м", "в", "о", "с"],
  ];

  const resultText = "еьеаатосзокбразросоуктемвос";

  return [
    {
      stage: 1,
      type: "summary",
      title: "Исходные данные",
      data: {
        sourceText: "скоросубботаазатемвоскресенье",
        readMode: "змейкой с верхнего правого угла",
        resultText,
      },
    },
    {
      stage: 2,
      type: "matrixSpiralWrite",
      title: "Запись текста в матрицу",
      data: {
        matrix,
        startCell: { row: 3, col: 2 },
      },
    },
    {
      stage: 3,
      type: "matrixSpiralRead",
      title: "Чтение матрицы",
      data: {
        matrix,
        startCell: { row: 0, col: 4 },
      },
    },
    {
      stage: 4,
      type: "matrixFinal",
      title: "Итоговая таблица",
      data: {
        matrix,
      },
    },
    {
      stage: 5,
      type: "summary",
      title: "Получившийся текст",
      data: {
        resultText,
      },
    },
  ];
}

function getSubstitutionMockSteps() {
  const shiftedAlphabets = getShiftedAlphabets(8);
  const inputText = "нетакиеметеливлицолетели";
  const letters = inputText.toUpperCase().split("");
  const indexes = letters.map((_, index) => index % 8);

  const replaceRows = letters.map((letter, index) => {
    const alphabetIndex = RUS_ALPHABET.indexOf(letter);
    const rowIndex = index % 8;
    const result =
      alphabetIndex >= 0 ? shiftedAlphabets[rowIndex][alphabetIndex] : letter;

    return {
      source: letter,
      rowIndex,
      alphabetIndex,
      result,
    };
  });

  const resultText = replaceRows.map((item) => item.result).join("");

  return [
    {
      stage: 1,
      type: "summary",
      title: "Исходные данные",
      data: {
        shift: 8,
        slogan: "ЛОПАТА",
        sourceText: inputText,
      },
    },
    {
      stage: 2,
      type: "alphabetTable",
      title: "Таблица получившихся алфавитов",
      data: {
        sourceAlphabet: RUS_ALPHABET,
        shiftedAlphabets,
      },
    },
    {
      stage: 3,
      type: "indexedText",
      title: "Пронумерованные буквы исходного текста",
      data: {
        indexes,
        letters,
      },
    },
    {
      stage: 4,
      type: "replaceSteps",
      title: "Процесс замены",
      data: replaceRows,
    },
    {
      stage: 5,
      type: "summary",
      title: "Получившийся текст",
      data: {
        resultText,
      },
    },
  ];
}

function Cipher() {
  const [mode, setMode] = useState("substitution");
  const [action, setAction] = useState("encrypt");
  const [shift, setShift] = useState(8);
  const [slogan, setSlogan] = useState("ЛОПАТА");
  const [order, setOrder] = useState("snake_top_right");
  const [inputText, setInputText] = useState("нетакиеметеливлицолетели");

  const [resultSteps, setResultSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);

  const currentStepData = resultSteps[currentStep];

  const buttonState = useMemo(() => {
    return {
      canGoPrev: currentStep > 0,
      canGoNext: currentStep < resultSteps.length - 1,
      hasSteps: resultSteps.length > 0,
    };
  }, [currentStep, resultSteps]);

  const applyMockForMode = (newMode) => {
    if (newMode === "substitution") {
      setAction("encrypt");
      setShift(8);
      setSlogan("ЛОПАТА");
      setOrder("snake_top_right");
      setInputText("нетакиеметеливлицолетели");
    }

    if (newMode === "transposition") {
      setAction("encrypt");
      setShift(8);
      setSlogan("ЛОПАТА");
      setOrder("snake_top_right");
      setInputText("скоросубботаазатемвоскресенье");
    }

    if (newMode === "combined_sp") {
      setAction("encrypt");
      setShift(8);
      setSlogan("ЛОПАТА");
      setOrder("snake_top_right");
      setInputText("нетакиеметеливлицолетели");
    }

    if (newMode === "combined_ps") {
      setAction("encrypt");
      setShift(8);
      setSlogan("ЛОПАТА");
      setOrder("snake_top_right");
      setInputText("скоросубботаазатемвоскресенье");
    }

    setResultSteps([]);
    setCurrentStep(0);
  };

  const handleModeChange = (e) => {
    const newMode = e.target.value;
    setMode(newMode);
    applyMockForMode(newMode);
  };

  const processText = () => {
    if (mode === "substitution") {
      setResultSteps(getSubstitutionMockSteps());
      setCurrentStep(0);
      return;
    }

    if (mode === "transposition") {
      setResultSteps(getTranspositionMockSteps());
      setCurrentStep(0);
      return;
    }

    if (mode === "combined_sp") {
      const substitutionSteps = getSubstitutionMockSteps();
      const transpositionSteps = getTranspositionMockSteps().map((step) => ({
        ...step,
        stage: step.stage + 10,
      }));

      setResultSteps([
        {
          stage: 0,
          type: "summary",
          title: "Комбинированный режим",
          data: {
            sourceText: inputText,
            readMode: "Сначала: замена, потом: перестановка",
          },
        },
        ...substitutionSteps,
        ...transpositionSteps,
      ]);
      setCurrentStep(0);
      return;
    }

    if (mode === "combined_ps") {
      const transpositionSteps = getTranspositionMockSteps();
      const substitutionSteps = getSubstitutionMockSteps().map((step) => ({
        ...step,
        stage: step.stage + 10,
      }));

      setResultSteps([
        {
          stage: 0,
          type: "summary",
          title: "Комбинированный режим",
          data: {
            sourceText: inputText,
            readMode: "Сначала: перестановка, потом: замена",
          },
        },
        ...transpositionSteps,
        ...substitutionSteps,
      ]);
      setCurrentStep(0);
    }
  };

  const prevStep = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  };

  const nextStep = () => {
    setCurrentStep((prev) => Math.min(prev + 1, resultSteps.length - 1));
  };

  const nextStage = () => {
    if (!currentStepData) return;

    const nextIndex = resultSteps.findIndex(
      (step, index) =>
        index > currentStep &&
        Number(step.stage) > Number(currentStepData.stage),
    );

    if (nextIndex !== -1) {
      setCurrentStep(nextIndex);
    }
  };

  const resetStage = () => {
    if (!currentStepData) return;

    const firstIndexOfCurrentStage = resultSteps.findIndex(
      (step) => step.stage === currentStepData.stage,
    );

    if (firstIndexOfCurrentStage !== -1) {
      setCurrentStep(firstIndexOfCurrentStage);
    }
  };

  const resetAll = () => {
    setCurrentStep(0);
  };

  const renderCurrentStep = () => {
    if (!currentStepData) {
      return (
        <div className="empty-result">
          Здесь появится результат выполнения мок-сценария.
        </div>
      );
    }

    switch (currentStepData.type) {
      case "summary":
        return (
          <SummaryStep
            title={currentStepData.title}
            data={currentStepData.data}
          />
        );
      case "matrixSpiral":
        return (
          <MatrixSpiralStep
            title={currentStepData.title}
            data={currentStepData.data}
          />
        );
      case "matrixFinal":
        return (
          <MatrixStep
            title={currentStepData.title}
            data={currentStepData.data}
          />
        );
      case "alphabetTable":
        return (
          <AlphabetTableStep
            title={currentStepData.title}
            data={currentStepData.data}
          />
        );
      case "indexedText":
        return (
          <IndexedTextStep
            title={currentStepData.title}
            data={currentStepData.data}
          />
        );
      case "replaceSteps":
        return (
          <ReplaceStepsStep
            title={currentStepData.title}
            data={currentStepData.data}
          />
        );
      case "matrixSpiralWrite":
        return (
          <MatrixSpiralStep
            title={currentStepData.title}
            data={currentStepData.data}
            variant="write"
          />
        );

      case "matrixSpiralRead":
        return (
          <MatrixSpiralStep
            title={currentStepData.title}
            data={currentStepData.data}
            variant="read"
          />
        );
      default:
        return <div>Неизвестный тип шага</div>;
    }
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
          <select id="mode" value={mode} onChange={handleModeChange}>
            {modeOptions.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>

          <label htmlFor="action">Действие</label>
          <select
            id="action"
            value={action}
            onChange={(e) => setAction(e.target.value)}
          >
            {actionOptions.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>

          {mode === "substitution" && (
            <>
              <label htmlFor="shift">Ключ замены</label>
              <input
                type="number"
                id="shift"
                value={shift}
                min="1"
                max="32"
                onChange={(e) => setShift(Number(e.target.value))}
              />

              <label htmlFor="slogan">Лозунг</label>
              <textarea
                id="slogan"
                rows="2"
                value={slogan}
                onChange={(e) => setSlogan(e.target.value)}
              />

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
              <label htmlFor="order">Порядок чтения матрицы</label>
              <select
                id="order"
                value={order}
                onChange={(e) => setOrder(e.target.value)}
              >
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

          {mode === "combined_sp" && (
            <>
              <h3 className="section-mini-title">Сначала: шифр замены</h3>

              <label htmlFor="shift">Ключ замены</label>
              <input
                type="number"
                id="shift"
                value={shift}
                min="1"
                max="32"
                onChange={(e) => setShift(Number(e.target.value))}
              />

              <label htmlFor="slogan">Лозунг</label>
              <textarea
                id="slogan"
                rows="2"
                value={slogan}
                onChange={(e) => setSlogan(e.target.value)}
              />

              <h3 className="section-mini-title">Потом: шифр перестановки</h3>

              <label htmlFor="order">Порядок чтения матрицы</label>
              <select
                id="order"
                value={order}
                onChange={(e) => setOrder(e.target.value)}
              >
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

          {mode === "combined_ps" && (
            <>
              <h3 className="section-mini-title">Сначала: шифр перестановки</h3>

              <label htmlFor="order">Порядок чтения матрицы</label>
              <select
                id="order"
                value={order}
                onChange={(e) => setOrder(e.target.value)}
              >
                {orderOptions.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>

              <h3 className="section-mini-title">Потом: шифр замены</h3>

              <label htmlFor="shift">Ключ замены</label>
              <input
                type="number"
                id="shift"
                value={shift}
                min="1"
                max="32"
                onChange={(e) => setShift(Number(e.target.value))}
              />

              <label htmlFor="slogan">Лозунг</label>
              <textarea
                id="slogan"
                rows="2"
                value={slogan}
                onChange={(e) => setSlogan(e.target.value)}
              />

              <label htmlFor="sourceText">Исходный текст</label>
              <textarea
                id="sourceText"
                rows="7"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />
            </>
          )}

          <button className="btn full" onClick={processText}>
            Выполнить
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
            <button
              className="btn small-btn"
              onClick={prevStep}
              disabled={!buttonState.canGoPrev}
            >
              Предыдущий шаг
            </button>

            <button
              className="btn small-btn"
              onClick={nextStep}
              disabled={!buttonState.canGoNext}
            >
              Следующий шаг
            </button>

            <button
              className="btn small-btn"
              onClick={nextStage}
              disabled={!buttonState.hasSteps}
            >
              К следующему этапу
            </button>

            <button
              className="btn small-btn"
              onClick={resetStage}
              disabled={!buttonState.hasSteps}
            >
              В начало этапа
            </button>

            <button
              className="btn small-btn"
              onClick={resetAll}
              disabled={!buttonState.hasSteps}
            >
              В самое начало
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

function SummaryStep({ title, data }) {
  return (
    <div className="step-view">
      <h3 className="step-title">{title}</h3>

      <div className="summary-list">
        {data.shift !== undefined && (
          <div className="summary-item">
            <span className="summary-label">Ключ замены:</span>
            <span>{data.shift}</span>
          </div>
        )}

        {data.slogan && (
          <div className="summary-item">
            <span className="summary-label">Лозунг:</span>
            <span>{data.slogan}</span>
          </div>
        )}

        {data.sourceText && (
          <div className="summary-item">
            <span className="summary-label">Исходный текст:</span>
            <span>{data.sourceText}</span>
          </div>
        )}

        {data.readMode && (
          <div className="summary-item">
            <span className="summary-label">Способ чтения:</span>
            <span>{data.readMode}</span>
          </div>
        )}

        {data.resultText && (
          <div className="summary-item summary-item-result">
            <span className="summary-label">Получившийся текст:</span>
            <span>{data.resultText}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function MatrixSpiralStep({ title, data, variant }) {
  const isWrite = variant === "write";

  return (
    <div className="step-view">
      <h3 className="step-title">{title}</h3>

      <p className="muted-text">
        {isWrite
          ? "Показано, как текст записывается в матрицу."
          : "Показано, как матрица читается змейкой с верхнего правого угла."}
      </p>

      <p className="muted-text">
        Начальная точка: {data.startCell.col + 1} столбец,{" "}
        {data.startCell.row + 1} строка
      </p>

      <SpiralMatrix matrix={data.matrix} variant={variant} hideLetters />
    </div>
  );
}
function MatrixStep({ title, data }) {
  return (
    <div className="step-view">
      <h3 className="step-title">{title}</h3>

      <div className="table-wrap">
        <table className="matrix-table clean-light-table">
          <tbody>
            {data.matrix.map((row, rowIndex) => (
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

function SpiralMatrix({ matrix, variant = "write", hideLetters = false }) {
  const rows = matrix.length;
  const cols = matrix[0].length;
  const cellSize = 70;
  const width = cols * cellSize;
  const height = rows * cellSize;

  const getCellCenter = (row, col) => ({
    x: col * cellSize + cellSize / 2,
    y: row * cellSize + cellSize / 2,
  });

  const buildPathFromCells = (cells) => {
    if (!cells.length) return "";

    const first = getCellCenter(cells[0].row, cells[0].col);
    let d = `M ${first.x} ${first.y}`;

    for (let i = 1; i < cells.length; i += 1) {
      const point = getCellCenter(cells[i].row, cells[i].col);
      d += ` L ${point.x} ${point.y}`;
    }

    return d;
  };

  // Запись в матрицу — оставляем старую спираль/обход
  const writeCells = [
    { row: 3, col: 2 },
    { row: 2, col: 2 },
    { row: 2, col: 1 },
    { row: 3, col: 1 },
    { row: 4, col: 1 },
    { row: 4, col: 2 },
    { row: 4, col: 3 },
    { row: 3, col: 3 },
    { row: 2, col: 3 },
    { row: 1, col: 3 },
    { row: 1, col: 2 },
    { row: 1, col: 1 },
    { row: 1, col: 0 },
    { row: 2, col: 0 },
    { row: 3, col: 0 },
    { row: 4, col: 0 },
    { row: 5, col: 0 },
    { row: 5, col: 1 },
    { row: 5, col: 2 },
    { row: 5, col: 3 },
    { row: 5, col: 4 },
    { row: 4, col: 4 },
    { row: 3, col: 4 },
    { row: 2, col: 4 },
    { row: 1, col: 4 },
    { row: 0, col: 4 },
    { row: 0, col: 3 },
    { row: 0, col: 2 },
    { row: 0, col: 1 },
    { row: 0, col: 0 },
  ];

  // Чтение матрицы — вертикальная змейка с верхнего правого угла
  const readCells = [
    { row: 0, col: 4 },
    { row: 1, col: 4 },
    { row: 2, col: 4 },
    { row: 3, col: 4 },
    { row: 4, col: 4 },
    { row: 5, col: 4 },

    { row: 5, col: 3 },
    { row: 4, col: 3 },
    { row: 3, col: 3 },
    { row: 2, col: 3 },
    { row: 1, col: 3 },
    { row: 0, col: 3 },

    { row: 0, col: 2 },
    { row: 1, col: 2 },
    { row: 2, col: 2 },
    { row: 3, col: 2 },
    { row: 4, col: 2 },
    { row: 5, col: 2 },

    { row: 5, col: 1 },
    { row: 4, col: 1 },
    { row: 3, col: 1 },
    { row: 2, col: 1 },
    { row: 1, col: 1 },
    { row: 0, col: 1 },

    { row: 0, col: 0 },
    { row: 1, col: 0 },
    { row: 2, col: 0 },
    { row: 3, col: 0 },
    { row: 4, col: 0 },
    { row: 5, col: 0 },
  ];

  const cells = variant === "read" ? readCells : writeCells;
  const pathD = buildPathFromCells(cells);

  const isMarkedCell = (row, col) =>
    cells.some((cell) => cell.row === row && cell.col === col);

  const startCell = cells[0];
  const startCenter = getCellCenter(startCell.row, startCell.col);

  return (
    <div className="spiral-wrapper">
      <div
        className="spiral-table-box"
        style={{ width: `${width}px`, height: `${height}px` }}
      >
        <table
          className="matrix-table spiral-html-table"
          style={{ width: `${width}px`, height: `${height}px` }}
        >
          <tbody>
            {matrix.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((cell, colIndex) => {
                  const className = isMarkedCell(rowIndex, colIndex)
                    ? "spiral-path-cell"
                    : "";

                  return (
                    <td
                      key={colIndex}
                      className={className}
                      style={{
                        width: `${cellSize}px`,
                        height: `${cellSize}px`,
                      }}
                    >
                      {hideLetters ? "" : cell || ""}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>

        <svg
          className="spiral-overlay"
          width={width}
          height={height}
          viewBox={`0 0 ${width} ${height}`}
        >
          <defs>
            <marker
              id={`arrowhead-${variant}`}
              markerWidth="12"
              markerHeight="12"
              refX="10"
              refY="6"
              orient="auto"
            >
              <path d="M 0 0 L 12 6 L 0 12 L 4 6 z" fill="#b00020" />
            </marker>
          </defs>

          <path
            d={pathD}
            fill="none"
            stroke="#b00020"
            strokeWidth="4"
            strokeLinecap="round"
            strokeLinejoin="round"
            markerEnd={`url(#arrowhead-${variant})`}
          />

          <text
            x={startCenter.x}
            y={startCenter.y + 10}
            textAnchor="middle"
            fontSize="34"
            fontWeight="700"
            fill="#b00020"
          >
            ×
          </text>
        </svg>
      </div>
    </div>
  );
}
function AlphabetTableStep({ title, data }) {
  return (
    <div className="step-view">
      <h3 className="step-title">{title}</h3>

      <div className="table-wrap">
        <table className="alphabet-table clean-light-table">
          <tbody>
            <tr>
              <td></td>
              {data.sourceAlphabet.map((letter, index) => (
                <td key={`source-${index}`}>{letter}</td>
              ))}
            </tr>

            {data.shiftedAlphabets.map((row, rowIndex) => (
              <tr key={`row-${rowIndex}`}>
                <td>{rowIndex}</td>
                {row.map((letter, colIndex) => (
                  <td key={`cell-${rowIndex}-${colIndex}`}>{letter}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function IndexedTextStep({ title, data }) {
  return (
    <div className="step-view">
      <h3 className="step-title">{title}</h3>

      <div className="table-wrap">
        <table className="indexed-table clean-light-table">
          <tbody>
            <tr>
              {data.indexes.map((item, index) => (
                <td key={`index-${index}`}>{item}</td>
              ))}
            </tr>
            <tr>
              {data.letters.map((item, index) => (
                <td key={`letter-${index}`}>{item}</td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ReplaceStepsStep({ title, data }) {
  return (
    <div className="step-view">
      <h3 className="step-title">{title}</h3>

      <div className="table-wrap">
        <table className="process-table clean-light-table">
          <thead>
            <tr>
              <th>№</th>
              <th>Буква</th>
              <th>Номер строки</th>
              <th>Номер алфавита</th>
              <th>=</th>
              <th>Получившаяся буква</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={index}>
                <td>{index + 1}</td>
                <td>{item.source}</td>
                <td>{item.rowIndex}</td>
                <td>{item.alphabetIndex}</td>
                <td>=</td>
                <td>{item.result}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Cipher;
