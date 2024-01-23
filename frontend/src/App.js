import React, { useState } from 'react';
import './App.css';
import JSONTreeView from './JSONTreeView';
import axios from 'axios';

function App() {
  const [fileContent, setFileContent] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

  const handlePreviewClick = async () => {
    console.log(selectedFile);
    try {
      const response = await axios.get(`http://localhost:5000/file_preview?location=${encodeURIComponent(selectedFile.location)}`);
      setFileContent(response.data.content);
    } catch (error) {
      console.error('Error fetching file content: ', error);
      setFileContent('');
  }
  };

  const handleDownloadClick = () => {
    if (!selectedFile) {
      alert('No file selected for download.');
      return;
    }
    
    const downloadUrl = `http://localhost:5000/file_download?location=${encodeURIComponent(selectedFile.location)}`;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', selectedFile.name); 
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
  };
  

  // Don't preview if the files are 3D
  const previewAvailable = selectedFile && !(selectedFile.name.endsWith(".stl") || selectedFile.name.endsWith(".step") || selectedFile.name.endsWith(".ply"));

  return (
    <div className="App">
      <div className="app-content">
        <JSONTreeView setSelectedFile={setSelectedFile} setFileContent={setFileContent} selectedFile={selectedFile}/>
        <div className="content-display">
          <div className="file-actions">
            {selectedFile && (
              <>
                <button onClick={handlePreviewClick} disabled={!previewAvailable}>
                  Preview {selectedFile.name}
                </button>
                <button onClick={handleDownloadClick}>
                  Download {selectedFile.name}
                </button>
              </>
            )}
          </div>
          <pre>{selectedFile && !previewAvailable ? "3D files are not available for preview" : fileContent}</pre>
        </div>
      </div>
    </div>
  );
}

export default App;
