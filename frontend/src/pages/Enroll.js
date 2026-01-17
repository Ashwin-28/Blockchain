import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import { enrollSubject, checkLiveness } from '../services/api';
import './Enroll.css';

function Enroll() {
  const webcamRef = useRef(null);
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [biometricType, setBiometricType] = useState('facial');
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
    setStep(3);
  }, [webcamRef]);

  const retake = () => {
    setCapturedImage(null);
    setStep(2);
  };

  const handleEnroll = async () => {
    if (!capturedImage || !name) return;
    
    setIsProcessing(true);
    setError(null);
    
    try {
      // Convert base64 to blob
      const response = await fetch(capturedImage);
      const blob = await response.blob();
      const file = new File([blob], 'biometric.jpg', { type: 'image/jpeg' });
      
      // Check liveness first
      const liveness = await checkLiveness(file);
      if (!liveness.is_live) {
        setError('Liveness check failed. Please ensure you are using a live capture.');
        setIsProcessing(false);
        return;
      }
      
      // Enroll
      const enrollResult = await enrollSubject(file, name, biometricType);
      setResult(enrollResult);
      setStep(4);
    } catch (err) {
      setError(err.response?.data?.error || 'Enrollment failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="page enroll-page">
      <div className="container">
        <div className="page-header text-center">
          <span className="mono-label">Identity Registration</span>
          <h1>Biometric Enrollment</h1>
          <p className="text-muted">
            Register your biometric identity on the blockchain
          </p>
        </div>

        {/* Progress Steps */}
        <div className="progress-steps">
          <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>
            <span className="step-num">1</span>
            <span>Details</span>
          </div>
          <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>
            <span className="step-num">2</span>
            <span>Capture</span>
          </div>
          <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>
            <span className="step-num">3</span>
            <span>Confirm</span>
          </div>
          <div className={`progress-step ${step >= 4 ? 'active' : ''}`}>
            <span className="step-num">4</span>
            <span>Complete</span>
          </div>
        </div>

        <div className="enroll-content card">
          {/* Step 1: Details */}
          {step === 1 && (
            <div className="step-content">
              <h3>Enter Your Details</h3>
              <div className="form-group">
                <label className="label">Full Name</label>
                <input
                  type="text"
                  className="input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter your name"
                />
              </div>
              <div className="form-group">
                <label className="label">Biometric Type</label>
                <div className="biometric-options">
                  {['facial', 'fingerprint', 'iris'].map((type) => (
                    <button
                      key={type}
                      className={`option-btn ${biometricType === type ? 'selected' : ''}`}
                      onClick={() => setBiometricType(type)}
                    >
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              <button
                className="btn btn-primary"
                onClick={() => setStep(2)}
                disabled={!name}
              >
                Continue to Capture
              </button>
            </div>
          )}

          {/* Step 2: Capture */}
          {step === 2 && (
            <div className="step-content">
              <h3>Capture Your Biometric</h3>
              <p className="text-muted mb-lg">
                Position yourself in good lighting using webcam OR upload a photo
              </p>
              <div className="webcam-container">
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  videoConstraints={{ facingMode: 'user' }}
                  className="webcam"
                />
                <div className="webcam-overlay">
                  <div className="face-guide"></div>
                </div>
              </div>
              
              <div className="action-buttons centered">
                <button className="btn btn-primary" onClick={capture}>
                  Capture from Webcam
                </button>
                
                <div className="upload-btn-wrapper">
                  <input
                    type="file"
                    accept="image/*"
                    id="file-upload"
                    style={{ display: 'none' }}
                    onChange={(e) => {
                      const file = e.target.files[0];
                      if (file) {
                        const reader = new FileReader();
                        reader.onloadend = () => {
                          setCapturedImage(reader.result);
                          setStep(3);
                        };
                        reader.readAsDataURL(file);
                      }
                    }}
                  />
                  <button 
                    className="btn btn-outline"
                    onClick={() => document.getElementById('file-upload').click()}
                  >
                    Upload Image
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Confirm */}
          {step === 3 && (
            <div className="step-content">
              <h3>Confirm Your Capture</h3>
              <div className="captured-preview">
                <img src={capturedImage} alt="Captured biometric" />
              </div>
              {error && <div className="error-message">{error}</div>}
              <div className="action-buttons">
                <button className="btn btn-outline" onClick={retake}>
                  Retake
                </button>
                <button
                  className="btn btn-primary"
                  onClick={handleEnroll}
                  disabled={isProcessing}
                >
                  {isProcessing ? 'Processing...' : 'Enroll on Blockchain'}
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Complete */}
          {step === 4 && result && (
            <div className="step-content text-center">
              <div className="success-icon">✓</div>
              <h3>Enrollment Successful!</h3>
              <p className="text-muted">Your biometric identity has been registered</p>
              
              <div className="result-details card-glass">
                <div className="result-item">
                  <span className="result-label">Subject ID</span>
                  <span className="result-value mono">{result.subject_id?.slice(0, 16)}...</span>
                </div>
                <div className="result-item">
                  <span className="result-label">Biometric Type</span>
                  <span className="result-value">{result.biometric_type}</span>
                </div>
                {result.transaction_hash && (
                  <div className="result-item">
                    <span className="result-label">Transaction</span>
                    <span className="result-value mono">{result.transaction_hash?.slice(0, 16)}...</span>
                  </div>
                )}
              </div>
              
              <p className="important-note">
                ⚠️ Save your Subject ID - you'll need it for authentication
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Enroll;
