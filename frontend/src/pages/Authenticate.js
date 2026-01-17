import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import { authenticateSubject } from '../services/api';
import './Authenticate.css';

function Authenticate() {
  const webcamRef = useRef(null);
  const [subjectId, setSubjectId] = useState('');
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
  }, [webcamRef]);

  const reset = () => {
    setCapturedImage(null);
    setResult(null);
    setError(null);
  };

  const handleAuthenticate = async () => {
    if (!capturedImage || !subjectId) return;
    
    setIsProcessing(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await fetch(capturedImage);
      const blob = await response.blob();
      const file = new File([blob], 'biometric.jpg', { type: 'image/jpeg' });
      
      const authResult = await authenticateSubject(file, subjectId, 'facial');
      setResult(authResult);
    } catch (err) {
      setError(err.response?.data?.error || 'Authentication failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="page auth-page">
      <div className="container">
        <div className="page-header text-center">
          <span className="mono-label">Identity Verification</span>
          <h1>Authenticate</h1>
          <p className="text-muted">
            Verify your identity against the blockchain record
          </p>
        </div>

        <div className="auth-layout">
          {/* Input Section */}
          <div className="auth-input card">
            <h3>Subject ID</h3>
            <input
              type="text"
              className="input"
              value={subjectId}
              onChange={(e) => setSubjectId(e.target.value)}
              placeholder="Enter your subject ID"
            />
            
            <div className="gold-line"></div>
            
            <h3>Biometric Capture</h3>
            
            {!capturedImage ? (
              <div className="webcam-container">
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  videoConstraints={{ facingMode: 'user' }}
                  className="webcam"
                />
                
                <div className="action-buttons centered mt-lg">
                  <button className="btn btn-primary" onClick={capture}>
                    Capture
                  </button>
                  
                  <div className="upload-btn-wrapper">
                    <input
                      type="file"
                      accept="image/*"
                      id="auth-file-upload"
                      style={{ display: 'none' }}
                      onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) {
                          const reader = new FileReader();
                          reader.onloadend = () => {
                            setCapturedImage(reader.result);
                          };
                          reader.readAsDataURL(file);
                        }
                      }}
                    />
                    <button 
                      className="btn btn-outline"
                      onClick={() => document.getElementById('auth-file-upload').click()}
                    >
                      Upload
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="captured-container">
                <img src={capturedImage} alt="Captured" className="captured-img" />
                <div className="capture-actions">
                  <button className="btn btn-outline" onClick={reset}>
                    Retake
                  </button>
                  <button
                    className="btn btn-primary"
                    onClick={handleAuthenticate}
                    disabled={!subjectId || isProcessing}
                  >
                    {isProcessing ? 'Verifying...' : 'Verify Identity'}
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Result Section */}
          <div className="auth-result card">
            <h3>Verification Result</h3>
            
            {!result && !error && (
              <div className="result-placeholder">
                <div className="placeholder-icon">🔍</div>
                <p>Capture your biometric and click verify to see results</p>
              </div>
            )}
            
            {error && (
              <div className="result-error">
                <div className="result-icon error">✕</div>
                <h4>Verification Failed</h4>
                <p>{error}</p>
              </div>
            )}
            
            {result && (
              <div className={`result-display ${result.authenticated ? 'success' : 'failure'}`}>
                <div className={`result-icon ${result.authenticated ? 'success' : 'error'}`}>
                  {result.authenticated ? '✓' : '✕'}
                </div>
                <h4>{result.authenticated ? 'Identity Verified' : 'Verification Failed'}</h4>
                <p>{result.message}</p>
                
                <div className="result-meta">
                  <div className="meta-item">
                    <span className="meta-label">Subject ID</span>
                    <span className="meta-value">{result.subject_id?.slice(0, 16)}...</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Logged on Chain</span>
                    <span className="meta-value">{result.logged_on_chain ? 'Yes' : 'No'}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Authenticate;
