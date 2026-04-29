import React, { useEffect, useState } from 'react'
import { getAllDocuments, getDocument } from '../api'
import Loading from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/EmptyState'
import DocumentCard from '../components/DocumentCard'

// Documents list and details page
export default function DocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Load documents on mount
  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const docs = await getAllDocuments()
        setDocuments(docs)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  // Open a document detail
  async function openDocument(id) {
    setLoading(true)
    setError(null)
    try {
      const doc = await getDocument(id)
      setSelected(doc)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Loading message="Loading documents..." />
  if (error) return <ErrorMessage error={error} />

  return (
    <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="md:col-span-1 space-y-3">
        <h3 className="text-lg font-semibold">Documents</h3>
        {documents.length === 0 && <EmptyState title="No documents" description="Upload PDFs to begin." />}
        <div className="space-y-2">
          {documents.map(d => (
            <DocumentCard key={d.id} doc={d} onOpen={openDocument} />
          ))}
        </div>
      </div>

      <div className="md:col-span-2">
        <h3 className="text-lg font-semibold">Details</h3>
        {selected ? (
          <div className="p-4 bg-white border rounded">
            <div className="font-medium">{selected.filename}</div>
            <div className="text-sm text-slate-600 mt-2">Path: {selected.file_path}</div>
            <div className="mt-2">Chunks: {selected.chunk_count}</div>
            <div>Embeddings: {selected.embedding_count}</div>
            <div>Size: {selected.file_size} bytes</div>
          </div>
        ) : (
          <EmptyState title="Select a document" description="Choose a document to view details." />
        )}
      </div>
    </div>
  )
}
