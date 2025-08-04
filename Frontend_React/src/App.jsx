// import React, { useState } from 'react'

// import './App.css'
// import FileUpload from './Components/FileUpload';
// import Navbar from './Components/Navbar';
// import Footer from './Components/footer';

// function App() {
//   const [downloadUrl, setDownloadUrl] = useState(null);

//   const handleFileUpload = async (file) => {
//     const formData = new FormData();
//     formData.append("file", file);

//     const res = await fetch("http://127.0.0.1:8000/process-file", {
//       method: "POST",
//       body: formData,
//     })
  
//   // Convert response to a downloadable blob
//     const blob = await res.blob();
//     const url = window.URL.createObjectURL(blob);
//     setDownloadUrl(url);
//   };

//   return (
//   <>
//       <Navbar/>

//      <div className="p-6 max-w-3xl mx-auto text-center">
//       <h1 className="text-2xl font-bold mb-4">Pipeline Data Processing</h1>
//       <FileUpload onFileUpload={handleFileUpload} />

//       {downloadUrl && (
//         <a
//           href={downloadUrl}
//           download="processed_results.xlsx"
//           className="mt-4 inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
//         >
//           Download Processed File
//         </a>
//       )}
//     </div>

//     <Footer/>
//   </>
//   )
// }

// export default App

import React, { useState } from "react";
import "./App.css";
import FileUploader from "./Components/FileUploader";
import AnalysisSelector from "./Components/AnalysisSelector";
import ThresholdInputs from "./Components/ThresholdInputs";
import DownloadButton from "./Components/DownloadButton";
import Header from "./Components/Header";
// import Footer from "./Components/Footer";

const App = () => {
  const [file, setFile] = useState(null);
  const [selectedAnalyses, setSelectedAnalyses] = useState([]);
  const [thresholds, setThresholds] = useState({
    ACPSP: 4,
    Attenuation: 2,
    CPCIPS: -1.0,
  });

  return (
    
    <div className="container">
       <Header/> 
      <h1>Pipeline Data Processor</h1>
      <FileUploader onFileChange={setFile} />
      <AnalysisSelector
        selectedAnalyses={selectedAnalyses}
        onChange={setSelectedAnalyses}
      />
      <ThresholdInputs thresholds={thresholds} setThresholds={setThresholds} />
      <DownloadButton
        file={file}
        analyses={selectedAnalyses}
        thresholds={thresholds}
      />
      {/* <Footer/> */}
    </div>
  );
};

export default App;
