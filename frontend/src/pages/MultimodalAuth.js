import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import './MultimodalAuth.css';

/**
 * Multimodal Biometric Fusion Authentication
 * Combines multiple biometric modalities for enhanced security
 */
function MultimodalAuth() {
    const [activeModality, setActiveModality] = useState(null);
    const [biometricData, setBiometricData] = useState({
        face: null,
        fingerprint: null,
        voice: null,
        iris: null
    });
    const [fusionResult, setFusionResult] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const webcamRef = useRef(null);
    const [isRecording, setIsRecording] = useState(false);

    const modalities = [
        {
            id: 'face',
            name: 'Facial Recognition',
            icon: '👤',
            weight: 0.35,
            accuracy: '99.2%',
            description: 'CNN-based facial feature extraction'
        },
        {
            id: 'fingerprint',
            name: 'Fingerprint Scan',
            icon: '👆',
            weight: 0.30,
            accuracy: '99.8%',
            description: 'Minutiae-based fingerprint matching'
        },
        {
            id: 'voice',
            name: 'Voice Recognition',
            icon: '🎤',
            weight: 0.20,
            accuracy: '97.5%',
            description: 'Voice biometric analysis'
        },
        {
            id: 'iris',
            name: 'Iris Scan',
            icon: '👁️',
            weight: 0.15,
            accuracy: '99.9%',
            description: 'Iris pattern recognition'
        }
    ];

    const captureFace = () => {
        const imageSrc = webcamRef.current.getScreenshot();
        setBiometricData(prev => ({ ...prev, face: imageSrc }));
        setActiveModality(null);
    };

    const captureFingerprint = () => {
        // Simulate fingerprint capture
        setBiometricData(prev => ({
            ...prev,
            fingerprint: 'data:image/png;base64,simulated_fingerprint_data'
        }));
        setActiveModality(null);
    };

    const captureVoice = () => {
        setIsRecording(true);
        // Simulate voice recording
        setTimeout(() => {
            setBiometricData(prev => ({
                ...prev,
                voice: 'audio_data_captured'
            }));
            setIsRecording(false);
            setActiveModality(null);
        }, 3000);
    };

    const captureIris = () => {
        const imageSrc = webcamRef.current.getScreenshot();
        setBiometricData(prev => ({ ...prev, iris: imageSrc }));
        setActiveModality(null);
    };

    const performFusion = async () => {
        setIsProcessing(true);

        // Simulate multimodal fusion processing
        await new Promise(resolve => setTimeout(resolve, 2500));

        const capturedModalities = Object.entries(biometricData).filter(([_, value]) => value !== null);
        const modalityScores = capturedModalities.map(([key, _]) => {
            const modality = modalities.find(m => m.id === key);
            return {
                name: modality.name,
                score: 0.85 + Math.random() * 0.14, // 85-99% match
                weight: modality.weight
            };
        });

        // Calculate weighted fusion score
        const totalWeight = modalityScores.reduce((sum, m) => sum + m.weight, 0);
        const fusionScore = modalityScores.reduce((sum, m) => sum + (m.score * m.weight), 0) / totalWeight;

        setFusionResult({
            success: fusionScore > 0.90,
            fusionScore: fusionScore,
            modalityScores: modalityScores,
            timestamp: new Date().toISOString(),
            method: 'Weighted Score-Level Fusion',
            confidence: fusionScore > 0.95 ? 'Very High' : fusionScore > 0.90 ? 'High' : 'Medium'
        });

        setIsProcessing(false);
    };

    const reset = () => {
        setBiometricData({
            face: null,
            fingerprint: null,
            voice: null,
            iris: null
        });
        setFusionResult(null);
        setActiveModality(null);
    };

    const capturedCount = Object.values(biometricData).filter(v => v !== null).length;

    return (
        <div className="page multimodal-page">
            <div className="container">
                {/* Header */}
                <div className="multimodal-header fade-up">
                    <div className="mono-label">🔬 Advanced Biometrics</div>
                    <h1>Multimodal Biometric Fusion</h1>
                    <p className="multimodal-subtitle">
                        Combine multiple biometric modalities for maximum security and accuracy.
                        Achieve 99.99% authentication accuracy with weighted fusion algorithms.
                    </p>
                </div>

                {/* Modality Grid */}
                {!fusionResult && (
                    <div className="modality-grid fade-up">
                        {modalities.map(modality => (
                            <div
                                key={modality.id}
                                className={`modality-card card ${biometricData[modality.id] ? 'captured' : ''} ${activeModality === modality.id ? 'active' : ''}`}
                                onClick={() => !biometricData[modality.id] && setActiveModality(modality.id)}
                            >
                                <div className="modality-icon">{modality.icon}</div>
                                <h3>{modality.name}</h3>
                                <div className="modality-stats">
                                    <div className="stat">
                                        <span className="stat-label">Weight</span>
                                        <span className="stat-value">{(modality.weight * 100).toFixed(0)}%</span>
                                    </div>
                                    <div className="stat">
                                        <span className="stat-label">Accuracy</span>
                                        <span className="stat-value text-gold">{modality.accuracy}</span>
                                    </div>
                                </div>
                                <p className="modality-description text-muted">{modality.description}</p>
                                {biometricData[modality.id] && (
                                    <div className="capture-badge">
                                        <span>✓ Captured</span>
                                    </div>
                                )}
                                {!biometricData[modality.id] && (
                                    <button className="btn btn-outline btn-sm mt-md">
                                        Capture {modality.name}
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Capture Modal */}
                {activeModality && (
                    <div className="capture-modal card-glass fade-up">
                        <h3>Capture {modalities.find(m => m.id === activeModality)?.name}</h3>

                        {(activeModality === 'face' || activeModality === 'iris') && (
                            <div className="webcam-container">
                                <Webcam
                                    ref={webcamRef}
                                    audio={false}
                                    screenshotFormat="image/jpeg"
                                    className="webcam-feed"
                                />
                                <div className="webcam-overlay">
                                    {activeModality === 'face' && <div className="face-guide"></div>}
                                    {activeModality === 'iris' && <div className="iris-guide"></div>}
                                </div>
                            </div>
                        )}

                        {activeModality === 'fingerprint' && (
                            <div className="fingerprint-scanner">
                                <div className="scanner-animation">
                                    <div className="scan-line"></div>
                                </div>
                                <p className="text-muted mt-md">Place your finger on the scanner</p>
                            </div>
                        )}

                        {activeModality === 'voice' && (
                            <div className="voice-recorder">
                                <div className={`voice-animation ${isRecording ? 'recording' : ''}`}>
                                    <div className="voice-wave"></div>
                                    <div className="voice-wave"></div>
                                    <div className="voice-wave"></div>
                                </div>
                                <p className="text-muted mt-md">
                                    {isRecording ? 'Recording... Please say: "My voice is my password"' : 'Click to start recording'}
                                </p>
                            </div>
                        )}

                        <div className="button-group mt-xl">
                            <button className="btn btn-outline" onClick={() => setActiveModality(null)}>
                                Cancel
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={() => {
                                    if (activeModality === 'face') captureFace();
                                    else if (activeModality === 'fingerprint') captureFingerprint();
                                    else if (activeModality === 'voice') captureVoice();
                                    else if (activeModality === 'iris') captureIris();
                                }}
                                disabled={isRecording}
                            >
                                {isRecording ? 'Recording...' : 'Capture'}
                            </button>
                        </div>
                    </div>
                )}

                {/* Fusion Button */}
                {!fusionResult && capturedCount > 0 && !activeModality && (
                    <div className="fusion-control fade-up">
                        <div className="fusion-status">
                            <span className="status-text">
                                {capturedCount} of {modalities.length} modalities captured
                            </span>
                            <div className="progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{ width: `${(capturedCount / modalities.length) * 100}%` }}
                                ></div>
                            </div>
                        </div>
                        <button
                            className="btn btn-primary btn-lg"
                            onClick={performFusion}
                            disabled={isProcessing || capturedCount < 2}
                        >
                            {isProcessing ? 'Processing Fusion...' : `Perform Fusion Authentication (${capturedCount} modalities)`}
                        </button>
                        {capturedCount < 2 && (
                            <p className="text-muted mt-md">Capture at least 2 modalities to perform fusion</p>
                        )}
                    </div>
                )}

                {/* Fusion Result */}
                {fusionResult && (
                    <div className="fusion-result card-glass fade-up">
                        <div className={`result-header ${fusionResult.success ? 'success' : 'failure'}`}>
                            <div className="result-icon">
                                {fusionResult.success ? '✓' : '✗'}
                            </div>
                            <h3>{fusionResult.success ? 'Authentication Successful' : 'Authentication Failed'}</h3>
                            <div className="fusion-score">
                                <div className="score-label">Fusion Score</div>
                                <div className="score-value">{(fusionResult.fusionScore * 100).toFixed(2)}%</div>
                                <div className="score-confidence">Confidence: {fusionResult.confidence}</div>
                            </div>
                        </div>

                        <div className="modality-scores">
                            <h4>Individual Modality Scores</h4>
                            {fusionResult.modalityScores.map((score, idx) => (
                                <div key={idx} className="score-item">
                                    <div className="score-info">
                                        <span className="score-name">{score.name}</span>
                                        <span className="score-weight">Weight: {(score.weight * 100).toFixed(0)}%</span>
                                    </div>
                                    <div className="score-bar">
                                        <div
                                            className="score-bar-fill"
                                            style={{ width: `${score.score * 100}%` }}
                                        ></div>
                                    </div>
                                    <span className="score-percentage">{(score.score * 100).toFixed(1)}%</span>
                                </div>
                            ))}
                        </div>

                        <div className="fusion-details mt-xl">
                            <div className="detail-item">
                                <span className="detail-label">Fusion Method</span>
                                <span className="detail-value">{fusionResult.method}</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Timestamp</span>
                                <span className="detail-value">{new Date(fusionResult.timestamp).toLocaleString()}</span>
                            </div>
                        </div>

                        <button className="btn btn-primary mt-xl" onClick={reset}>
                            Authenticate Again
                        </button>
                    </div>
                )}

                {/* Info Section */}
                <div className="fusion-info mt-2xl">
                    <h3 className="text-center mb-xl">Why Multimodal Fusion?</h3>
                    <div className="info-grid">
                        <div className="info-card card">
                            <div className="info-icon">🎯</div>
                            <h4>Higher Accuracy</h4>
                            <p className="text-muted">
                                Combining multiple biometrics achieves 99.99% accuracy, far exceeding single-modality systems.
                            </p>
                        </div>
                        <div className="info-card card">
                            <div className="info-icon">🛡️</div>
                            <h4>Spoof Resistance</h4>
                            <p className="text-muted">
                                Attackers must spoof multiple biometric types simultaneously, making attacks virtually impossible.
                            </p>
                        </div>
                        <div className="info-card card">
                            <div className="info-icon">⚖️</div>
                            <h4>Weighted Fusion</h4>
                            <p className="text-muted">
                                Each modality contributes based on its reliability, optimizing overall system performance.
                            </p>
                        </div>
                        <div className="info-card card">
                            <div className="info-icon">🔄</div>
                            <h4>Fallback Support</h4>
                            <p className="text-muted">
                                If one modality fails, others can compensate, ensuring reliable authentication.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default MultimodalAuth;
