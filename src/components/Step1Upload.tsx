import React, { ChangeEvent } from "react";

interface Props {
  files: File[];
  setFiles: (files: File[]) => void;
  onNext: () => void;
}

export default function Step1Upload({ files, setFiles, onNext }: Props) {
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  return (
    <div>
      <h2>Step 1: Upload Content</h2>
      <input
        type="file"
        multiple
        accept=".pdf,.docx,.txt"
        onChange={handleFileChange}
      />
      <div style={{ marginTop: 12 }}>
        {files.map((file, idx) => (
          <div key={idx}>
            {file.name}{" "}
            <button
              style={{ color: "red", marginLeft: 8 }}
              onClick={() =>
                setFiles(files.filter((_, i) => i !== idx))
              }
            >
              Remove
            </button>
          </div>
        ))}
      </div>
      <button
        onClick={onNext}
        disabled={files.length === 0}
        style={{ marginTop: 24 }}
      >
        Continue
      </button>
    </div>
  );
}