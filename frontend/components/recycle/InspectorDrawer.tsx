'use client'

import { useState } from 'react'

interface InspectorData {
  id: string
  type: 'project' | 'task' | 'node'
  name: string
  details: Record<string, any>
}

export function InspectorDrawer() {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedItem, setSelectedItem] = useState<InspectorData | null>(null)

  const sampleData: InspectorData = {
    id: 'project-1',
    type: 'project',
    name: 'Análisis de Documentos Legales',
    details: {
      status: 'En progreso',
      progress: 75,
      startTime: '2024-01-15 09:30:00',
      estimatedCompletion: '2024-01-15 15:30:00',
      documentsProcessed: 45,
      totalDocuments: 60,
      currentPhase: 'Extracción de entidades',
      assignedNodes: ['node-1', 'node-2'],
      quotasUsed: 1250,
      quotasRemaining: 750,
      errors: 0,
      warnings: 2
    }
  }

  const handleInspect = () => {
    setSelectedItem(sampleData)
    setIsOpen(true)
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Inspector</h2>
        <button
          onClick={handleInspect}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Inspeccionar Proyecto
        </button>
      </div>

      {!isOpen && (
        <div className="text-center text-gray-500 py-8">
          <div className="mb-4">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p>Selecciona un elemento para inspeccionar sus detalles</p>
        </div>
      )}

      {isOpen && selectedItem && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="font-semibold text-lg">{selectedItem.name}</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="border rounded-lg p-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-600">Tipo:</span>
                <span className="ml-2 capitalize">{selectedItem.type}</span>
              </div>
              <div>
                <span className="font-medium text-gray-600">ID:</span>
                <span className="ml-2 font-mono">{selectedItem.id}</span>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="font-medium">Detalles</h4>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {Object.entries(selectedItem.details).map(([key, value]) => (
                <div key={key} className="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
                  <span className="font-medium text-gray-600 capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}:
                  </span>
                  <span className="text-right">
                    {Array.isArray(value) ? value.join(', ') : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex space-x-2">
            <button className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
              Exportar
            </button>
            <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Editar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

