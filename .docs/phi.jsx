import { useState, useEffect, useRef, useCallback } from "react";

const FIB = [1, 2];
for (let i = 2; i < 25; i++) FIB.push(FIB[i - 1] + FIB[i - 2]);

const NUM_DIGITS = 16;

function toZeckendorf(n) {
  if (n === 0) return new Array(NUM_DIGITS).fill(0);
  const digits = new Array(NUM_DIGITS).fill(0);
  let rem = n;
  for (let i = NUM_DIGITS - 1; i >= 0; i--) {
    if (FIB[i] <= rem) {
      digits[i] = 1;
      rem -= FIB[i];
    }
  }
  return digits;
}

function fromDigits(digits) {
  return digits.reduce((sum, d, i) => sum + d * (FIB[i] || 0), 0);
}

function rawAdd(a, b) {
  return a.map((v, i) => v + b[i]);
}

function findViolations(digits) {
  const violations = [];
  for (let i = 0; i < digits.length; i++) {
    if (digits[i] >= 2) violations.push({ type: "double", index: i });
  }
  for (let i = 0; i < digits.length - 1; i++) {
    if (digits[i] >= 1 && digits[i + 1] >= 1) violations.push({ type: "adjacent", indices: [i, i + 1] });
  }
  return violations;
}

function normalize(digits, maxLen) {
  const d = [...digits];
  while (d.length < maxLen) d.push(0);

  for (let i = 0; i < d.length; i++) {
    if (d[i] >= 2) {
      const sources = [i];
      const targets = [];
      if (i === 0) {
        d[0] -= 2;
        if (d.length <= 1) d.push(0);
        d[1] += 1;
        targets.push(1);
      } else if (i === 1) {
        d[1] -= 2;
        if (d.length <= 2) d.push(0);
        d[2] += 1;
        d[0] += 1;
        targets.push(2, 0);
      } else {
        d[i] -= 2;
        if (d.length <= i + 1) d.push(0);
        d[i + 1] += 1;
        d[i - 2] += 1;
        targets.push(i + 1, i - 2);
      }
      return { digits: d, rule: "double", index: i, sources, targets };
    }
  }

  for (let i = 0; i < d.length - 1; i++) {
    if (d[i] >= 1 && d[i + 1] >= 1) {
      d[i] -= 1;
      d[i + 1] -= 1;
      if (d.length <= i + 2) d.push(0);
      d[i + 2] += 1;
      return { digits: d, rule: "carry", index: i, sources: [i, i + 1], targets: [i + 2] };
    }
  }

  return null;
}

function fullNormalize(digits) {
  const steps = [{ digits: [...digits], rule: null, index: null, sources: [], targets: [] }];
  let current = [...digits];
  let safety = 200;
  while (safety-- > 0) {
    const result = normalize(current, NUM_DIGITS + 4);
    if (!result) break;
    current = result.digits;
    steps.push({
      digits: [...current],
      rule: result.rule,
      index: result.index,
      sources: result.sources,
      targets: result.targets
    });
  }
  return steps;
}

const GOLD = "#d4a017";
const RED = "#e04040";
const GREEN = "#40c878";
const ORANGE = "#ffa028";
const MONO = "'JetBrains Mono', monospace";
const SERIF = "'Crimson Pro', Georgia, serif";

function Cell({ value, weight, status }) {
  let bg, border, glow, textColor;

  if (status === "source") {
    bg = "rgba(224,64,64,0.2)";
    border = `2px solid ${RED}`;
    glow = `0 0 10px rgba(224,64,64,0.5)`;
    textColor = RED;
  } else if (status === "target") {
    bg = "rgba(64,200,120,0.2)";
    border = `2px solid ${GREEN}`;
    glow = `0 0 10px rgba(64,200,120,0.5)`;
    textColor = GREEN;
  } else if (status === "violation-double") {
    bg = "rgba(224,64,64,0.12)";
    border = `1px dashed ${RED}`;
    glow = "none";
    textColor = RED;
  } else if (status === "violation-adjacent") {
    bg = "rgba(255,160,40,0.12)";
    border = `1px dashed ${ORANGE}`;
    glow = "none";
    textColor = ORANGE;
  } else if (status === "settled" && value > 0) {
    bg = "rgba(64,200,120,0.1)";
    border = `1px solid rgba(64,200,120,0.4)`;
    glow = "0 0 8px rgba(64,200,120,0.2)";
    textColor = GREEN;
  } else if (value > 0) {
    bg = "rgba(212,160,23,0.12)";
    border = "1px solid rgba(212,160,23,0.35)";
    glow = "none";
    textColor = GOLD;
  } else {
    bg = "rgba(255,255,255,0.02)";
    border = "1px solid rgba(255,255,255,0.06)";
    glow = "none";
    textColor = "rgba(255,255,255,0.12)";
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 3, transition: "all 0.3s ease" }}>
      <div style={{ fontSize: 9, color: "rgba(212,160,23,0.4)", fontFamily: MONO }}>F({weight})</div>
      <div
        style={{
          width: 42,
          height: 42,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: bg,
          border,
          borderRadius: 6,
          fontFamily: MONO,
          fontSize: value >= 2 ? 20 : 17,
          color: textColor,
          fontWeight: value > 0 ? 700 : 400,
          transition: "all 0.3s ease",
          boxShadow: glow,
          position: "relative"
        }}
      >
        {value}
        {status === "source" && (
          <div
            style={{
              position: "absolute",
              top: -7,
              right: -7,
              width: 15,
              height: 15,
              background: RED,
              borderRadius: "50%",
              fontSize: 10,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              fontWeight: 700,
              lineHeight: 1
            }}
          >
            −
          </div>
        )}
        {status === "target" && (
          <div
            style={{
              position: "absolute",
              top: -7,
              right: -7,
              width: 15,
              height: 15,
              background: GREEN,
              borderRadius: "50%",
              fontSize: 10,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              fontWeight: 700,
              lineHeight: 1
            }}
          >
            +
          </div>
        )}
      </div>
      <div style={{ fontSize: 8, color: "rgba(255,255,255,0.2)", fontFamily: MONO }}>{FIB[weight] ?? ""}</div>
    </div>
  );
}

function Register({ digits, sources, targets, violations, settled }) {
  const maxIdx = Math.max(7, digits.reduce((m, v, i) => (v !== 0 ? Math.max(m, i) : m), 0) + 1);
  const visible = digits.slice(0, Math.min(maxIdx + 1, NUM_DIGITS));

  const violationSet = new Map();
  (violations || []).forEach(v => {
    if (v.type === "double") violationSet.set(v.index, "violation-double");
    if (v.type === "adjacent")
      v.indices.forEach(idx => {
        if (!violationSet.has(idx)) violationSet.set(idx, "violation-adjacent");
      });
  });
  const srcSet = new Set(sources || []);
  const tgtSet = new Set(targets || []);

  function getStatus(i) {
    if (srcSet.has(i)) return "source";
    if (tgtSet.has(i)) return "target";
    if (settled) return "settled";
    if (violationSet.has(i)) return violationSet.get(i);
    return "normal";
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "row-reverse",
        gap: 5,
        justifyContent: "flex-end",
        flexWrap: "wrap"
      }}
    >
      {visible
        .map((v, i) => (
          <Cell
            key={i}
            value={v}
            weight={i}
            status={getStatus(i)}
          />
        ))
        .reverse()}
    </div>
  );
}

function RuleBanner({ step, isSettled, isRaw }) {
  if (isSettled)
    return (
      <div
        style={{
          padding: "10px 16px",
          background: "rgba(64,200,120,0.08)",
          border: `1px solid rgba(64,200,120,0.3)`,
          borderRadius: 8,
          marginBottom: 14,
          fontFamily: MONO,
          fontSize: 12,
          color: GREEN,
          letterSpacing: 1,
          display: "flex",
          alignItems: "center",
          gap: 10
        }}
      >
        <span style={{ fontSize: 18 }}>⬡</span>
        <span>SETTLED — valid Zeckendorf form</span>
      </div>
    );

  if (isRaw)
    return (
      <div
        style={{
          padding: "10px 16px",
          background: "rgba(212,160,23,0.06)",
          border: "1px solid rgba(212,160,23,0.2)",
          borderRadius: 8,
          marginBottom: 14,
          fontFamily: MONO,
          fontSize: 12,
          color: "rgba(212,160,23,0.7)",
          letterSpacing: 1
        }}
      >
        RAW SUM — cell-wise addition, not yet normalized
      </div>
    );

  const { rule, index } = step;
  if (rule === "carry") {
    return (
      <div
        style={{
          padding: "10px 16px",
          background: "rgba(212,160,23,0.06)",
          border: "1px solid rgba(212,160,23,0.25)",
          borderRadius: 8,
          marginBottom: 14,
          fontFamily: MONO
        }}
      >
        <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: 1, marginBottom: 4, color: GOLD }}>
          CARRY — adjacent 1s merge upward
        </div>
        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)" }}>
          <span style={{ color: RED }}>
            F({index}) + F({index + 1})
          </span>
          {" → "}
          <span style={{ color: GREEN }}>F({index + 2})</span>
          <span style={{ color: "rgba(255,255,255,0.3)", marginLeft: 12 }}>
            {FIB[index]} + {FIB[index + 1]} = {FIB[index + 2]}
          </span>
        </div>
      </div>
    );
  }

  if (rule === "double") {
    let eqn;
    if (index === 0) {
      eqn = (
        <>
          <span style={{ color: RED }}>2×F(0)</span>
          {" → "}
          <span style={{ color: GREEN }}>F(1)</span>
          <span style={{ color: "rgba(255,255,255,0.3)", marginLeft: 12 }}>
            2×{FIB[0]} = {FIB[1]}
          </span>
        </>
      );
    } else if (index === 1) {
      eqn = (
        <>
          <span style={{ color: RED }}>2×F(1)</span>
          {" → "}
          <span style={{ color: GREEN }}>F(2) + F(0)</span>
          <span style={{ color: "rgba(255,255,255,0.3)", marginLeft: 12 }}>
            2×{FIB[1]} = {FIB[2]}+{FIB[0]}
          </span>
        </>
      );
    } else {
      eqn = (
        <>
          <span style={{ color: RED }}>2×F({index})</span>
          {" → "}
          <span style={{ color: GREEN }}>
            F({index + 1}) + F({index - 2})
          </span>
          <span style={{ color: "rgba(255,255,255,0.3)", marginLeft: 12 }}>
            2×{FIB[index]} = {FIB[index + 1]}+{FIB[index - 2]}
          </span>
        </>
      );
    }
    return (
      <div
        style={{
          padding: "10px 16px",
          background: "rgba(224,64,64,0.05)",
          border: "1px solid rgba(224,64,64,0.25)",
          borderRadius: 8,
          marginBottom: 14,
          fontFamily: MONO
        }}
      >
        <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: 1, marginBottom: 4, color: RED }}>
          RESOLVE — double splits apart
        </div>
        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)" }}>{eqn}</div>
      </div>
    );
  }

  return null;
}

export default function PhiRegister() {
  const [a, setA] = useState(7);
  const [b, setB] = useState(5);
  const [steps, setSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [mode, setMode] = useState("idle");
  const timerRef = useRef(null);

  const compute = useCallback(() => {
    const zA = toZeckendorf(a);
    const zB = toZeckendorf(b);
    const raw = rawAdd(zA, zB);
    const normSteps = fullNormalize(raw);
    setSteps(normSteps);
    setCurrentStep(0);
    setMode("result");
    setPlaying(false);
  }, [a, b]);

  useEffect(() => {
    if (playing && currentStep < steps.length - 1) {
      timerRef.current = setTimeout(() => setCurrentStep(s => s + 1), 800);
      return () => clearTimeout(timerRef.current);
    } else if (playing && currentStep >= steps.length - 1) {
      setPlaying(false);
    }
  }, [playing, currentStep, steps.length]);

  const play = () => {
    if (steps.length === 0) return;
    if (currentStep >= steps.length - 1) setCurrentStep(0);
    setPlaying(true);
  };

  const current = steps[currentStep] || { digits: [], rule: null, index: null, sources: [], targets: [] };
  const isSettled = currentStep === steps.length - 1 && steps.length > 0;
  const isRaw = currentStep === 0;
  const zA = toZeckendorf(a);
  const zB = toZeckendorf(b);
  const currentViolations = isSettled ? [] : findViolations(current.digits);

  const inputStyle = {
    width: 72,
    padding: "8px 10px",
    background: "rgba(255,255,255,0.05)",
    border: "1px solid rgba(212,160,23,0.3)",
    borderRadius: 6,
    color: GOLD,
    fontFamily: MONO,
    fontSize: 16,
    textAlign: "center",
    outline: "none"
  };
  const btnBase = {
    padding: "8px 18px",
    border: "1px solid rgba(212,160,23,0.4)",
    borderRadius: 6,
    background: "rgba(212,160,23,0.1)",
    color: GOLD,
    cursor: "pointer",
    fontFamily: MONO,
    fontSize: 12,
    letterSpacing: 1,
    transition: "all 0.2s ease"
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0a0a0c", color: "#e8e0d0", padding: "32px 24px", fontFamily: SERIF }}>
      <link
        href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@300;400;600&family=JetBrains+Mono:wght@400;700&display=swap"
        rel="stylesheet"
      />

      <div style={{ maxWidth: 740, margin: "0 auto" }}>
        <div style={{ marginBottom: 36, textAlign: "center" }}>
          <h1
            style={{
              fontSize: 28,
              fontWeight: 300,
              color: GOLD,
              margin: 0,
              letterSpacing: 6,
              textTransform: "uppercase",
              fontFamily: SERIF
            }}
          >
            φ-Register
          </h1>
          <div style={{ fontSize: 11, color: "rgba(212,160,23,0.4)", marginTop: 6, fontFamily: MONO, letterSpacing: 3 }}>
            FIBONACCI-WEIGHTED ARITHMETIC
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 16, marginBottom: 28 }}>
          <input
            type="number"
            min={0}
            max={300}
            value={a}
            onChange={e => {
              setA(Math.min(300, Math.max(0, +e.target.value || 0)));
              setMode("idle");
            }}
            style={inputStyle}
          />
          <span style={{ fontSize: 20, color: GOLD, fontWeight: 300 }}>+</span>
          <input
            type="number"
            min={0}
            max={300}
            value={b}
            onChange={e => {
              setB(Math.min(300, Math.max(0, +e.target.value || 0)));
              setMode("idle");
            }}
            style={inputStyle}
          />
          <button
            onClick={compute}
            style={{ ...btnBase, background: "rgba(212,160,23,0.2)" }}
          >
            POUR
          </button>
        </div>

        {/* Source registers */}
        <div
          style={{
            padding: 16,
            background: "rgba(255,255,255,0.02)",
            borderRadius: 10,
            border: "1px solid rgba(255,255,255,0.05)",
            marginBottom: 16
          }}
        >
          <div style={{ fontSize: 11, color: "rgba(212,160,23,0.5)", marginBottom: 6, fontFamily: MONO, letterSpacing: 2 }}>
            A = {a}
          </div>
          <Register digits={zA} />
          <div style={{ marginTop: 5, fontSize: 13, color: "rgba(255,255,255,0.45)", fontFamily: MONO }}>
            = {fromDigits(zA)}
          </div>

          <div style={{ height: 12 }} />

          <div style={{ fontSize: 11, color: "rgba(212,160,23,0.5)", marginBottom: 6, fontFamily: MONO, letterSpacing: 2 }}>
            B = {b}
          </div>
          <Register digits={zB} />
          <div style={{ marginTop: 5, fontSize: 13, color: "rgba(255,255,255,0.45)", fontFamily: MONO }}>
            = {fromDigits(zB)}
          </div>
        </div>

        {/* Cascade */}
        {mode === "result" && steps.length > 0 && (
          <div
            style={{
              padding: 20,
              background: "rgba(212,160,23,0.02)",
              borderRadius: 10,
              border: "1px solid rgba(212,160,23,0.12)",
              marginBottom: 16
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
              <div style={{ fontSize: 10, fontFamily: MONO, color: "rgba(255,255,255,0.25)", letterSpacing: 2 }}>
                NORMALIZATION CASCADE
              </div>
              <div style={{ fontSize: 11, fontFamily: MONO, color: "rgba(255,255,255,0.3)" }}>
                {currentStep + 1} / {steps.length}
              </div>
            </div>

            <RuleBanner
              step={current}
              isSettled={isSettled}
              isRaw={isRaw}
            />

            <div style={{ fontSize: 11, color: "rgba(212,160,23,0.5)", marginBottom: 6, fontFamily: MONO, letterSpacing: 2 }}>
              A + B
            </div>
            <Register
              digits={current.digits}
              sources={isRaw ? [] : current.sources}
              targets={isRaw ? [] : current.targets}
              violations={currentViolations}
              settled={isSettled}
            />
            <div style={{ marginTop: 5, fontSize: 13, color: "rgba(255,255,255,0.45)", fontFamily: MONO }}>
              = {fromDigits(current.digits)}
            </div>

            {/* Violation count */}
            {!isSettled && currentViolations.length > 0 && (
              <div style={{ fontSize: 10, fontFamily: MONO, color: "rgba(255,160,40,0.6)", marginTop: 6 }}>
                {currentViolations.length} violation{currentViolations.length > 1 ? "s" : ""} remaining
                {" · "}
                {currentViolations.map((v, i) => (
                  <span key={i}>
                    {v.type === "double" ?
                      <span style={{ color: RED }}>2× at F({v.index})</span>
                    : <span style={{ color: ORANGE }}>
                        adj F({v.indices[0]}),F({v.indices[1]})
                      </span>
                    }
                    {i < currentViolations.length - 1 ? " · " : ""}
                  </span>
                ))}
              </div>
            )}

            {/* Controls */}
            <div style={{ display: "flex", gap: 8, justifyContent: "center", marginTop: 14 }}>
              <button
                onClick={() => {
                  setPlaying(false);
                  setCurrentStep(s => Math.max(0, s - 1));
                }}
                disabled={currentStep === 0}
                style={{ ...btnBase, opacity: currentStep === 0 ? 0.3 : 1 }}
              >
                ◁
              </button>
              <button
                onClick={playing ? () => setPlaying(false) : play}
                style={{ ...btnBase, minWidth: 80 }}
              >
                {playing ? "PAUSE" : "▷ PLAY"}
              </button>
              <button
                onClick={() => {
                  setPlaying(false);
                  setCurrentStep(s => Math.min(steps.length - 1, s + 1));
                }}
                disabled={currentStep >= steps.length - 1}
                style={{ ...btnBase, opacity: currentStep >= steps.length - 1 ? 0.3 : 1 }}
              >
                ▷
              </button>
            </div>

            {/* Step log */}
            <div
              style={{
                marginTop: 16,
                padding: 10,
                background: "rgba(0,0,0,0.3)",
                borderRadius: 6,
                maxHeight: 180,
                overflowY: "auto"
              }}
            >
              {steps.map((s, i) => {
                const vis = s.digits.slice(
                  0,
                  Math.max(
                    8,
                    s.digits.reduce((m, v, j) => (v ? Math.max(m, j + 1) : m), 0)
                  )
                );
                const isCurrent = i === currentStep;
                const viols = i < steps.length - 1 ? findViolations(s.digits) : [];
                return (
                  <div
                    key={i}
                    onClick={() => {
                      setPlaying(false);
                      setCurrentStep(i);
                    }}
                    style={{
                      fontSize: 11,
                      fontFamily: MONO,
                      padding: "4px 8px",
                      cursor: "pointer",
                      color: isCurrent ? "#fff" : "rgba(255,255,255,0.2)",
                      background: isCurrent ? "rgba(212,160,23,0.1)" : "transparent",
                      borderLeft: isCurrent ? `2px solid ${GOLD}` : "2px solid transparent",
                      borderRadius: 2,
                      transition: "all 0.15s ease",
                      marginBottom: 1,
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center"
                    }}
                  >
                    <span>
                      {i === 0 ?
                        "raw sum"
                      : s.rule === "carry" ?
                        <>
                          <span style={{ color: isCurrent ? GOLD : "inherit" }}>carry</span> F({s.index})+F({s.index + 1})→F(
                          {s.index + 2})
                        </>
                      : <>
                          <span style={{ color: isCurrent ? RED : "inherit" }}>2×</span> F({s.index})
                        </>
                      }
                    </span>
                    <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ color: isCurrent ? "rgba(255,255,255,0.5)" : "rgba(255,255,255,0.12)" }}>
                        [{vis.slice().reverse().join("")}]
                      </span>
                      {viols.length > 0 && (
                        <span
                          style={{
                            fontSize: 9,
                            padding: "1px 5px",
                            borderRadius: 3,
                            background: "rgba(255,160,40,0.15)",
                            color: ORANGE
                          }}
                        >
                          {viols.length}
                        </span>
                      )}
                      {viols.length === 0 && i === steps.length - 1 && (
                        <span
                          style={{
                            fontSize: 9,
                            padding: "1px 5px",
                            borderRadius: 3,
                            background: "rgba(64,200,120,0.15)",
                            color: GREEN
                          }}
                        >
                          ✓
                        </span>
                      )}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Legend */}
        <div
          style={{
            display: "flex",
            gap: 20,
            justifyContent: "center",
            flexWrap: "wrap",
            marginTop: 16,
            fontSize: 10,
            fontFamily: MONO,
            color: "rgba(255,255,255,0.3)"
          }}
        >
          {[
            [RED, `2px solid ${RED}`, "consumed"],
            [GREEN, `2px solid ${GREEN}`, "produced"],
            ["rgba(224,64,64,0.1)", `1px dashed ${RED}`, "double (2+)"],
            ["rgba(255,160,40,0.1)", `1px dashed ${ORANGE}`, "adjacent 1s"]
          ].map(([bg, bdr, label]) => (
            <span key={label}>
              <span
                style={{
                  display: "inline-block",
                  width: 10,
                  height: 10,
                  borderRadius: 2,
                  background: bg,
                  border: bdr,
                  marginRight: 4,
                  verticalAlign: "middle",
                  opacity: 0.6
                }}
              />{" "}
              {label}
            </span>
          ))}
        </div>

        {/* Reference table */}
        <details style={{ marginTop: 24 }}>
          <summary
            style={{ fontSize: 11, fontFamily: MONO, color: "rgba(212,160,23,0.4)", cursor: "pointer", letterSpacing: 2 }}
          >
            ZECKENDORF TABLE (1–30)
          </summary>
          <div
            style={{
              marginTop: 12,
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
              gap: 4,
              padding: 12,
              background: "rgba(0,0,0,0.2)",
              borderRadius: 6
            }}
          >
            {Array.from({ length: 30 }, (_, i) => i + 1).map(n => {
              const z = toZeckendorf(n);
              const maxI = z.reduce((m, v, j) => (v ? Math.max(m, j) : m), 0);
              const code = z
                .slice(0, maxI + 1)
                .reverse()
                .join("");
              const parts = z
                .reduce((acc, v, j) => (v ? [...acc, FIB[j]] : acc), [])
                .reverse()
                .join("+");
              return (
                <div
                  key={n}
                  style={{ fontSize: 11, fontFamily: MONO, color: "rgba(255,255,255,0.35)", padding: "2px 6px" }}
                >
                  <span style={{ color: "rgba(212,160,23,0.6)", display: "inline-block", width: 28 }}>{n}</span>
                  <span style={{ color: "rgba(212,160,23,0.35)", marginRight: 8 }}>{code}</span>
                  <span style={{ color: "rgba(255,255,255,0.2)" }}>{parts}</span>
                </div>
              );
            })}
          </div>
        </details>

        <div
          style={{
            marginTop: 20,
            padding: 14,
            background: "rgba(255,255,255,0.02)",
            borderRadius: 8,
            border: "1px solid rgba(255,255,255,0.04)"
          }}
        >
          <div style={{ fontSize: 10, fontFamily: MONO, color: "rgba(212,160,23,0.4)", letterSpacing: 2, marginBottom: 8 }}>
            THE SINGLE AXIOM — THREE READINGS
          </div>
          <div style={{ fontSize: 12, fontFamily: MONO, color: "rgba(255,255,255,0.3)", lineHeight: 2.0 }}>
            <div>
              <span style={{ color: GOLD }}>CARRY</span> F(k) + F(k+1) = F(k+2) — adjacent 1s merge upward
            </div>
            <div>
              <span style={{ color: RED }}>RESOLVE</span> 2·F(k) = F(k+1) + F(k−2) — doubles split apart
            </div>
            <div>
              <span style={{ color: "rgba(212,160,23,0.5)" }}>BORROW</span> F(k) = F(k−1) + F(k−2) — expand downward
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
