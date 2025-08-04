import React from "react";
import "../App.css";

const ThresholdInputs = ({ thresholds, setThresholds }) => {
  const updateThreshold = (key, value) => {
    setThresholds({ ...thresholds, [key]: value });
  };

  return (
    <div className="card">
      <label>Set Thresholds</label>
      <h5>ACPSP Threshold</h5>
      <input
        type="number"
        placeholder="ACPSP Threshold"
        value={thresholds.ACPSP}
        onChange={(e) => updateThreshold("ACPSP", e.target.value)}
      />

      <h5>Attenuation Threshold</h5>
      <input
        type="number"
        placeholder="Attenuation Threshold"
        value={thresholds.Attenuation}
        onChange={(e) => updateThreshold("Attenuation", e.target.value)}
      />

      <h5>CPCIPS Threshold</h5>
      <input
        type="number"
        placeholder="CPCIPS Threshold"
        value={thresholds.CPCIPS}
        onChange={(e) => updateThreshold("CPCIPS", e.target.value)}
      />
    </div>
  );
};

export default ThresholdInputs;
