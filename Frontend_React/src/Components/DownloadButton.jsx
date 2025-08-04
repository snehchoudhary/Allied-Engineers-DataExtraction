import React from "react";
import '../App.css';
import { processData } from "../api";

const DownloadButton = ({ file, analyses, thresholds }) => {
  const handleDownload = async () => {
    if (!file || analyses.length === 0) {
      alert("Please upload a file and select analyses.");
      return;
    }

    try {
      const blob = await processData(file, analyses, thresholds);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "Workbook.xlsx";
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (error) {
      alert("Error processing file");
    }
  };

  return <button onClick={handleDownload}>Download Processed Workbook</button>;
};

export default DownloadButton;
