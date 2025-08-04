import React from "react";
import "../App.css";

const FileUploader = ({ onFileChange }) => {
  return (
    <div className="card">
      <label>Upload Data File</label>
      <input
        type="file"
        accept=".xlsx,.xls,.csv"
        onChange={(e) => onFileChange(e.target.files[0])}
      />
    </div>
  );
};

export default FileUploader;
