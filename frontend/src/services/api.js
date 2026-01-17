import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "/api";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// Health & Status
export const checkHealth = async () => {
  const response = await api.get("/health");
  return response.data;
};

export const getBlockchainStatus = async () => {
  try {
    const response = await api.get("/blockchain/status");
    return response.data;
  } catch {
    return { connected: false };
  }
};

// Biometric Operations
export const extractBiometric = async (file, type = "facial") => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("type", type);

  const response = await api.post("/biometric/extract", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const checkLiveness = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/biometric/liveness", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

// Enrollment
export const enrollSubject = async (file, name, type = "facial") => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("name", name);
  formData.append("type", type);

  const response = await api.post("/enroll", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

// Authentication
export const authenticateSubject = async (file, subjectId, type = "facial") => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("subject_id", subjectId);
  formData.append("type", type);

  const response = await api.post("/authenticate", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

// Verification (1:1 comparison)
export const verifyBiometrics = async (file1, file2, type = "facial") => {
  const formData = new FormData();
  formData.append("file1", file1);
  formData.append("file2", file2);
  formData.append("type", type);

  const response = await api.post("/verify", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

// Statistics
export const getStats = async () => {
  const response = await api.get("/stats");
  return response.data;
};

// Database Explorer
export const getSubjects = async () => {
  const response = await api.get("/subjects");
  return response.data;
};

export const getAuthLogs = async () => {
  const response = await api.get("/auth-logs");
  return response.data;
};

// Blockchain Explorer
export const getBlockchainData = async () => {
  try {
    const response = await api.get("/blockchain/explorer");
    return response.data;
  } catch {
    return { blocks: [], transactions: [], accounts: [] };
  }
};

export default api;
