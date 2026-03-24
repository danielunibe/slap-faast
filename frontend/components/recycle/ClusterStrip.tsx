'use client'

import { useState, useEffect } from 'react'

interface Node {
  id: string
  cpu: number
  vram: number
  jobs: number
  status: 'active' | 'idle' | 'error'
}

export function ClusterStrip() {
  const [nodes, setNodes] = useState<Node[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simular carga de datos de nodos
    setTimeout(() => {
      setNodes([
        { id: 'node-1', cpu: 45, vram: 8192, jobs: 2, status: 'active' },
        { id: 'node-2', cpu: 78, vram: 16384, jobs: 4, status: 'active' },
        { id: 'node-3', cpu: 12, vram: 8192, jobs: 0, status: 'idle' },
        { id: 'node-4', cpu: 0, vram: 0, jobs: 0, status: 'error' }
      ])
      setLoading(false)
    }, 800)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'idle': return 'bg-yellow-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="space-y-2">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Estado del Cluster</h2>
      <div className="space-y-3">
        {nodes.map((node) => (
          <div key={node.id} className="flex items-center justify-between p-3 border rounded-lg">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(node.status)}`}></div>
              <span className="font-medium">{node.id}</span>
            </div>
            <div className="text-sm text-gray-600 space-y-1">
              <div>CPU: {node.cpu}%</div>
              <div>VRAM: {node.vram}MB</div>
              <div>Jobs: {node.jobs}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 pt-4 border-t">
        <div className="grid grid-cols-3 gap-4 text-center text-sm">
          <div>
            <div className="font-semibold text-green-600">{nodes.filter(n => n.status === 'active').length}</div>
            <div className="text-gray-500">Activos</div>
          </div>
          <div>
            <div className="font-semibold text-yellow-600">{nodes.filter(n => n.status === 'idle').length}</div>
            <div className="text-gray-500">Inactivos</div>
          </div>
          <div>
            <div className="font-semibold text-red-600">{nodes.filter(n => n.status === 'error').length}</div>
            <div className="text-gray-500">Error</div>
          </div>
        </div>
      </div>
    </div>
  )
}

