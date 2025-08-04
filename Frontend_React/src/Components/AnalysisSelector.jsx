import React from "react";
import "../App.css";

const ANALYSES = [
  "AC Interference",
  "ACPSP",
  "Attenuation",
  "CPCIPS",
  "Landuse"
];

const AnalysisSelector = ({ selectedAnalyses, onChange }) => {
  const handleCheckbox = (analysis) => {
    if (selectedAnalyses.includes(analysis)) {
      onChange(selectedAnalyses.filter((a) => a !== analysis));
    } else {
      onChange([...selectedAnalyses, analysis]);
    }
  };

  return (
    <div className="card">
      <label>Select Analyses</label>
      <div className="checkbox-group">
        {ANALYSES.map((analysis) => (
          <label key={analysis}>
            <input
              type="checkbox"
              checked={selectedAnalyses.includes(analysis)}
              onChange={() => handleCheckbox(analysis)}
            />{" "}
            {analysis}
          </label>
        ))}
      </div>
    </div>
  );
};

export default AnalysisSelector;
