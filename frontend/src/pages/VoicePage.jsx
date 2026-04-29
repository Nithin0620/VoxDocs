import React, { useState } from 'react'
import { speechToText, textToSpeech, downloadAudio } from '../api'
import Loading from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/EmptyState'

// Voice page: speech-to-text and text-to-speech
export default function VoicePage() {
  const [audioFile, setAudioFile] = useState(null)
  const [transcript, setTranscript] = useState(null)
  const [ttsText, setTtsText] = useState('')
  const [ttsResult, setTtsResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Handle audio selection
  function handleAudioChange(e) {
    setAudioFile(e.target.files[0])
    setTranscript(null)
    setError(null)
  }

  // Submit audio for transcription
  async function handleTranscribe(e) {
    e.preventDefault()
    if (!audioFile) return setError('Please select an audio file')
    setLoading(true)
    setError(null)
    try {
      const resp = await speechToText(audioFile)
      setTranscript(resp)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Convert text to speech
  async function handleTts(e) {
    e.preventDefault()
    if (!ttsText) return setError('Enter text to synthesize')
    setLoading(true)
    setError(null)
    setTtsResult(null)
    try {
      const resp = await textToSpeech(ttsText)
      setTtsResult(resp)
      // fetch audio blob and create URL for playback
      if (resp.audio_url) {
        // audio_url may be like /api/v1/audio/name.mp3 or /api/v1/audio/name
        const segments = resp.audio_url.split('/')
        const filename = segments[segments.length - 1]
        const url = await downloadAudio(filename)
        setTtsResult(prev => ({ ...prev, audio_blob_url: url }))
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h2 className="text-xl font-semibold">Voice Tools</h2>

      <div className="p-4 bg-white border rounded">
        <h4 className="font-medium">Speech to Text</h4>
        <form onSubmit={handleTranscribe} className="space-y-3 mt-3">
          <input onChange={handleAudioChange} type="file" accept="audio/*" />
          <div className="flex gap-2">
            <button disabled={loading} className="px-3 py-1 bg-slate-800 text-white rounded">Transcribe</button>
          </div>
        </form>
        {loading && <Loading message="Processing audio..." />}
        {error && <ErrorMessage error={error} />}
        {transcript ? (
          <div className="mt-3 p-3 bg-slate-50 border rounded">
            <div className="font-medium">Transcript</div>
            <div className="mt-2 text-slate-700">{transcript.text}</div>
            <div className="mt-1 text-sm text-slate-500">Language: {transcript.language} • Duration: {transcript.duration}s</div>
          </div>
        ) : <EmptyState title="No transcript" description="Transcribe an audio file to see text." />}
      </div>

      <div className="p-4 bg-white border rounded">
        <h4 className="font-medium">Text to Speech</h4>
        <form onSubmit={handleTts} className="space-y-3 mt-3">
          <textarea value={ttsText} onChange={e=>setTtsText(e.target.value)} rows={4} className="w-full p-2 border rounded" />
          <div className="flex gap-2">
            <button disabled={loading} className="px-3 py-1 bg-slate-800 text-white rounded">Synthesize</button>
          </div>
        </form>

        {ttsResult && (
          <div className="mt-3 p-3 bg-slate-50 border rounded">
            <div className="font-medium">Generated Speech</div>
            <div className="mt-2 text-slate-700">{ttsResult.text}</div>
            {ttsResult.audio_blob_url && (
              <audio controls className="mt-2">
                <source src={ttsResult.audio_blob_url} />
              </audio>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
