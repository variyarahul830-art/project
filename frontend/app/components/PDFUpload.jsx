'use client';

import { useState } from 'react';
import { uploadPDF, getPDFDocuments, deletePDF, downloadPDF } from '../services/api';

export default function PDFUpload() {
  const [file, setFile] = useState(null);
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pdfs, setPdfs] = useState([]);
  const [showList, setShowList] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        setError('Please select a valid PDF file');
        setFile(null);
        return;
      }
      if (selectedFile.size > 50 * 1024 * 1024) { // 50MB limit
        setError('File size must be less than 50MB');
        setFile(null);
        return;
      }
      setError(null);
      setFile(selectedFile);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    setIsLoading(true);
    setError(null);
    setMessage(null);

    try {
      const response = await uploadPDF(file, description);
      if (response.success) {
        setMessage(`✓ ${response.message}`);
        setFile(null);
        setDescription('');
        // Reset file input
        const fileInput = document.getElementById('pdf-file-input');
        if (fileInput) fileInput.value = '';
        // Refresh list if shown
        if (showList) {
          await loadPDFs();
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to upload PDF');
    } finally {
      setIsLoading(false);
    }
  };

  const loadPDFs = async () => {
    try {
      const documents = await getPDFDocuments();
      setPdfs(documents);
      setShowList(true);
    } catch (err) {
      setError('Failed to load PDF documents');
    }
  };

  const handleDelete = async (pdfId) => {
    if (!window.confirm('Are you sure you want to delete this PDF?')) {
      return;
    }

    try {
      await deletePDF(pdfId);
      setMessage('✓ PDF deleted successfully');
      await loadPDFs();
    } catch (err) {
      setError('Failed to delete PDF');
    }
  };

  const handleDownload = async (pdfId, filename) => {
    try {
      setError(null);
      const { blob, filename: downloadFilename } = await downloadPDF(pdfId);
      
      // Create a blob URL and trigger download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename || downloadFilename || 'document.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setMessage(`✓ Downloaded: ${filename || downloadFilename}`);
    } catch (err) {
      setError(err.message || 'Failed to download PDF');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="pdf-upload-container">
      <div className="pdf-upload-box">
        <h2>📄 Upload PDF</h2>
        
        <form onSubmit={handleUpload}>
          <div className="form-group">
            <label htmlFor="pdf-file-input">Select PDF File:</label>
            <input
              id="pdf-file-input"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={isLoading}
              className="file-input"
            />
            {file && <p className="file-name">Selected: {file.name}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="description">Description (Optional):</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add a description for this PDF..."
              disabled={isLoading}
              className="textarea"
              rows="3"
            />
          </div>

          <div className="button-group">
            <button 
              type="submit" 
              disabled={isLoading || !file}
              className="btn btn-primary"
            >
              {isLoading ? '⏳ Uploading...' : '📤 Upload PDF'}
            </button>
            <button
              type="button"
              onClick={loadPDFs}
              disabled={isLoading}
              className="btn btn-secondary"
            >
              📋 View All PDFs ({pdfs.length})
            </button>
          </div>
        </form>

        {message && <div className="message success">{message}</div>}
        {error && <div className="message error">{error}</div>}
      </div>

      {showList && (
        <div className="pdf-list-box">
          <h3>Uploaded PDFs</h3>
          {pdfs.length === 0 ? (
            <p className="no-pdfs">No PDFs uploaded yet</p>
          ) : (
            <div className="pdf-list">
              {pdfs.map((pdf) => (
                <div key={pdf.id} className="pdf-item">
                  <div className="pdf-info">
                    <h4>{pdf.filename}</h4>
                    <p className="file-meta">
                      Size: {formatFileSize(pdf.file_size)} | Uploaded: {formatDate(pdf.upload_date)}
                    </p>
                    {pdf.description && (
                      <p className="file-description">{pdf.description}</p>
                    )}
                    <p className="file-path">
                      <small>MinIO Path: {pdf.minio_path}</small>
                    </p>
                  </div>
                  <div className="pdf-actions">
                    <button
                      onClick={() => handleDownload(pdf.id, pdf.filename)}
                      className="btn btn-success"
                      disabled={isLoading}
                      title="Download PDF"
                    >
                      📥 Download
                    </button>
                    <button
                      onClick={() => handleDelete(pdf.id)}
                      className="btn btn-danger"
                      disabled={isLoading}
                      title="Delete PDF"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
          <button
            onClick={() => setShowList(false)}
            className="btn btn-secondary"
          >
            Close
          </button>
        </div>
      )}

      <style jsx>{`
        .pdf-upload-container {
          display: flex;
          flex-direction: column;
          gap: 20px;
          padding: 20px;
          width: 100%;
          max-width: 100%;
          overflow-y: auto;
          overflow-x: hidden;
          scroll-behavior: smooth;
        }

        .pdf-upload-container::-webkit-scrollbar {
          width: 10px;
        }

        .pdf-upload-container::-webkit-scrollbar-track {
          background: #f1f1f1;
        }

        .pdf-upload-container::-webkit-scrollbar-thumb {
          background: #888;
          border-radius: 5px;
        }

        .pdf-upload-container::-webkit-scrollbar-thumb:hover {
          background: #555;
        }

        .pdf-upload-box,
        .pdf-list-box {
          border: 2px solid #667eea;
          border-radius: 8px;
          padding: 20px;
          background: #f8f9fa;
        }

        .pdf-upload-box h2,
        .pdf-list-box h3 {
          color: #667eea;
          margin-bottom: 15px;
        }

        .form-group {
          margin-bottom: 15px;
        }

        .form-group label {
          display: block;
          margin-bottom: 8px;
          font-weight: 600;
          color: #333;
        }

        .file-input,
        .textarea {
          width: 100%;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-family: inherit;
          font-size: 14px;
        }

        .textarea {
          resize: vertical;
        }

        .file-input:disabled,
        .textarea:disabled {
          background-color: #e9ecef;
          cursor: not-allowed;
        }

        .file-name {
          margin-top: 5px;
          color: #28a745;
          font-size: 13px;
        }

        .button-group {
          display: flex;
          gap: 10px;
          margin-top: 20px;
        }

        .btn {
          flex: 1;
          padding: 10px 15px;
          border: none;
          border-radius: 4px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .btn-primary {
          background-color: #667eea;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background-color: #5568d3;
          transform: translateY(-2px);
        }

        .btn-secondary {
          background-color: #6c757d;
          color: white;
        }

        .btn-secondary:hover:not(:disabled) {
          background-color: #5a6268;
        }

        .btn-success {
          background-color: #28a745;
          color: white;
          padding: 8px 12px;
          font-size: 13px;
        }

        .btn-success:hover:not(:disabled) {
          background-color: #218838;
        }

        .btn-danger {
          background-color: #dc3545;
          color: white;
          padding: 8px 12px;
          font-size: 13px;
        }

        .btn-danger:hover:not(:disabled) {
          background-color: #c82333;
        }

        .btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .message {
          padding: 12px 15px;
          border-radius: 4px;
          margin-top: 15px;
          font-weight: 500;
        }

        .message.success {
          background-color: #d4edda;
          color: #155724;
          border: 1px solid #c3e6cb;
        }

        .message.error {
          background-color: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
        }

        .pdf-list {
          display: flex;
          flex-direction: column;
          gap: 15px;
          margin-bottom: 15px;
        }

        .pdf-item {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 15px;
          padding: 15px;
          background: white;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .pdf-info {
          flex: 1;
        }

        .pdf-actions {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          justify-content: flex-end;
          align-items: center;
        }

        .pdf-info h4 {
          margin: 0 0 5px 0;
          color: #333;
          word-break: break-word;
        }

        .file-meta {
          color: #666;
          font-size: 12px;
          margin: 5px 0;
        }

        .file-description {
          color: #555;
          font-size: 13px;
          margin: 8px 0 0 0;
          font-style: italic;
        }

        .file-path {
          color: #999;
          font-size: 11px;
          margin-top: 5px;
        }

        .no-pdfs {
          color: #999;
          text-align: center;
          padding: 20px;
        }
      `}</style>
    </div>
  );
}
