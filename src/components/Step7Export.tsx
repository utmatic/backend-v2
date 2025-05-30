import React from "react";

interface Props {
  outputs: any[];
  meta: any;
  onPrev: () => void;
  onRestart: () => void;
}

function toCSV(outputs: any[]): string {
  const header = ["Main Text", "CTA", "Link", "Full Text", "Char Count"];
  const rows = outputs.map((o) =>
    [
      o.main_text.replace(/"/g, '""'),
      o.cta_text.replace(/"/g, '""'),
      o.cta_link.replace(/"/g, '""'),
      o.full_text.replace(/"/g, '""'),
      o.char_count,
    ].map((x) => `"${x}"`).join(",")
  );
  return [header.join(","), ...rows].join("\n");
}

export default function Step7Export({ outputs, meta, onPrev, onRestart }: Props) {
  const handleCopy = () => {
    const all = outputs.map((o, i) =>
      `#${i + 1}\n${o.full_text}\n`
    ).join("\n");
    navigator.clipboard.writeText(all);
    alert("Copied to clipboard!");
  };

  const handleDownload = (type: "csv" | "txt") => {
    let content = "";
    let filename = "";
    if (type === "csv") {
      content = toCSV(outputs);
      filename = "repurposed_outputs.csv";
    } else {
      content = outputs.map((o, i) => `#${i + 1}\n${o.full_text}\n`).join("\n");
      filename = "repurposed_outputs.txt";
    }
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  };

  return (
    <div>
      <h2>Step 7: Export / Deploy</h2>
      <div>
        <button onClick={onPrev}>Back</button>{" "}
        <button onClick={onRestart}>Restart</button>
      </div>
      <div style={{ margin: "24px 0" }}>
        <button onClick={handleCopy}>Copy All to Clipboard</button>{" "}
        <button onClick={() => handleDownload("csv")}>Download as CSV</button>{" "}
        <button onClick={() => handleDownload("txt")}>Download as TXT</button>
      </div>
      <div>
        <h3>Preview</h3>
        {outputs.map((o, i) => (
          <div
            key={i}
            style={{
              border: "1px solid #ccc",
              margin: "12px 0",
              padding: 10,
              borderRadius: 6,
              background: "#fafafa",
            }}
          >
            <div>
              <strong>#{i + 1}</strong>
            </div>
            <div style={{ fontFamily: "monospace" }}>{o.full_text}</div>
            <div>
              <small>Char Count: {o.char_count}</small>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}