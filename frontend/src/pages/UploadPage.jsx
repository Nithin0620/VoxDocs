import React, { useState } from 'react'
import { uploadDocument, getUploadStatus } from '../api'
import Loading from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/EmptyState'

// Page to upload PDF documents and view processing status
export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [status, setStatus] = useState(null)

  // Handle file selection input
  function handleFileChange(e) {
    setFile(e.target.files[0])
    setResult(null)
    setError(null)
  }

  // Upload selected file
  async function handleUpload(e) {
    e.preventDefault()
    if (!file) return setError('Please select a PDF file to upload')

    setLoading(true)
    setError(null)
    try {
      const resp = await uploadDocument(file)
      setResult(resp)
      // fetch status after upload
      const st = await getUploadStatus()
      setStatus(st)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h2 className="text-xl font-semibold">Upload PDF</h2>

      <form onSubmit={handleUpload} className="p-4 bg-white border rounded space-y-4">
        <div>
          <label className="block text-sm font-medium">Select PDF</label>
          <input onChange={handleFileChange} type="file" accept="application/pdf" className="mt-2" />
        </div>

        <div className="flex items-center gap-2">
          <button disabled={loading} className="px-4 py-2 bg-slate-800 text-white rounded">Upload</button>
          <button type="button" onClick={async ()=>{ setLoading(true); try{ setStatus(await getUploadStatus()); }catch(e){setError(e.message)} finally{setLoading(false)} }} className="px-3 py-1 bg-slate-100 rounded">Refresh Status</button>
        </div>

        {loading && <Loading message="Uploading and processing..." />}
        {error && <ErrorMessage error={error} />}

        {result && (
          <div className="p-4 bg-green-50 border rounded">
            <div className="font-medium">Upload Result</div>
            <div>Filename: {result.filename}</div>
            <div>Chunks created: {result.chunks_created}</div>
          </div>
        )}

        {status ? (
          <div className="p-4 bg-white border rounded">
            <div className="font-medium">System Status</div>
            <pre className="text-sm text-slate-600">{JSON.stringify(status.statistics, null, 2)}</pre>
          </div>
        ) : (
          <EmptyState title="No status" description="Click 'Refresh Status' to check vector store and documents." />
        )}
      </form>
    </div>
  )
}
