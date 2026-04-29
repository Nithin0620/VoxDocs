import axios from 'axios'

// Base URL for backend API. Vite exposes environment variables through import.meta.env.
const BASE_ROOT = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_PREFIX = '/api/v1'
const AUTH_BASE = `${BASE_ROOT}${API_PREFIX}/auth`
const api = axios.create({
    baseURL: `${BASE_ROOT}${API_PREFIX}`,
    withCredentials: true,
    headers: {
        'Accept': 'application/json'
    }
})

// Helper to extract error message from axios errors
function getErrorMessage(error) {
    if (error.response && error.response.data) {
        return error.response.data.detail || error.response.data.message || error.response.data.error
    }
    return error.message || 'Unknown error'
}

export function getGoogleAuthUrl() {
    return `${AUTH_BASE}/google`
}

export async function signUp({ name, email, password }) {
    try {
        const resp = await api.post('/auth/signup', { name, email, password })
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

export async function signIn({ email, password }) {
    try {
        const resp = await api.post('/auth/login', { email, password })
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

export async function getCurrentUser() {
    try {
        const resp = await api.get('/auth/me')
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

export async function signOut() {
    try {
        const resp = await api.post('/auth/logout')
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

// Uploads a PDF file using multipart/form-data
export async function uploadDocument(file) {
    try {
        const formData = new FormData()
        formData.append('file', file)

        const resp = await api.post('/upload/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

// Get upload / rag status
export async function getUploadStatus() {
    try {
        const resp = await api.get('/upload/status')
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

// Documents
export async function getAllDocuments() {
    try {
        const resp = await api.get('/documents')
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

export async function getDocument(documentId) {
    try {
        const resp = await api.get(`/documents/${documentId}`)
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

export async function getDocumentStats() {
    try {
        const resp = await api.get('/documents/stats/overview')
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

// Query / Ask
export async function askQuestion(question, includeAudio = false) {
    try {
        const resp = await api.post('/ask/', { question, include_audio: includeAudio })
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

export async function askQuestionWithSession(sessionId, question, includeAudio = false) {
    try {
        const resp = await api.post('/ask/session', { session_id: sessionId, question, include_audio: includeAudio })
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

// Voice
export async function speechToText(file) {
    try {
        const formData = new FormData()
        formData.append('file', file)
        const resp = await api.post('/voice/speech-to-text', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

export async function textToSpeech(text) {
    try {
        const resp = await api.post('/voice/text-to-speech', { text })
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

// Download audio file as blob and return an object URL
export async function downloadAudio(filename) {
    try {
        const resp = await api.get(`/voice/audio/${filename}`, { responseType: 'blob' })
        const url = URL.createObjectURL(resp.data)
        return url
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

// Sessions
export async function createSession(title = null) {
    try {
        const resp = await api.post('/session/new', { title })
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

export async function getAllSessions() {
    try {
        const resp = await api.get('/session')
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

export async function getSessionHistory(sessionId) {
    try {
        const resp = await api.get(`/session/${sessionId}`)
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

export async function deleteSession(sessionId) {
    try {
        const resp = await api.delete(`/session/${sessionId}`)
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

// Health check (root)
export async function healthCheck() {
    try {
        const resp = await axios.get(`${BASE_ROOT}/health`)
        return resp.data
    } catch (err) {
        throw new Error(getErrorMessage(err))
    }
}

export default api
