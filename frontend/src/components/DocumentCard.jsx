import React from 'react'

// Card showing brief document metadata
export default function DocumentCard({ doc, onOpen }) {
  return (
    <div className="p-4 border bg-white rounded">
      <div className="flex items-center justify-between">
        <div>
          <div className="font-medium">{doc.filename}</div>
          <div className="text-sm text-slate-500">Uploaded: {new Date(doc.uploaded_at).toLocaleString()}</div>
        </div>
        <div className="text-sm text-slate-600">
          <button onClick={() => onOpen(doc.id)} className="px-3 py-1 bg-slate-100 rounded">View</button>
        </div>
      </div>
    </div>
  )
}
