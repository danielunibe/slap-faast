'use client'

import { useState, useEffect } from 'react'

interface DAGNode {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  x: number
  y: number
  dependencies: string[]
}

interface DAGEdge {
  from: string
  to: string
}

export function MiniDAG() {
  const [nodes, setNodes] = useState<DAGNode[]>([])
  const [edges, setEdges] = useState<DAGEdge[]>([])

  useEffect(() => {
    // Simular datos del DAG
    const sampleNodes: DAGNode[] = [
      { id: 'input', name: 'Entrada de Documentos', status: 'completed', x: 50, y: 50, dependencies: [] },
      { id: 'preprocess', name: 'Preprocesamiento', status: 'completed', x: 200, y: 50, dependencies: ['input'] },
      { id: 'extract', name: 'Extracción de Texto', status: 'running', x: 350, y: 30, dependencies: ['preprocess'] },
      { id: 'classify', name: 'Clasificación', status: 'running', x: 350, y: 90, dependencies: ['preprocess'] },
      { id: 'analyze', name: 'Análisis de Entidades', status: 'pending', x: 500, y: 50, dependencies: ['extract', 'classify'] },
      { id: 'output', name: 'Resultado Final', status: 'pending', x: 650, y: 50, dependencies: ['analyze'] }
    ]

    const sampleEdges: DAGEdge[] = [
      { from: 'input', to: 'preprocess' },
      { from: 'preprocess', to: 'extract' },
      { from: 'preprocess', to: 'classify' },
      { from: 'extract', to: 'analyze' },
      { from: 'classify', to: 'analyze' },
      { from: 'analyze', to: 'output' }
    ]

    setNodes(sampleNodes)
    setEdges(sampleEdges)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500 border-green-600'
      case 'running': return 'bg-blue-500 border-blue-600'
      case 'pending': return 'bg-gray-300 border-gray-400'
      case 'failed': return 'bg-red-500 border-red-600'
      default: return 'bg-gray-300 border-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        )
      case 'running':
        return (
          <svg className="w-4 h-4 text-white animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        )
      case 'failed':
        return (
          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        )
      default:
        return (
          <svg className="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
        )
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Flujo de Procesamiento (DAG)</h2>
      
      <div className="relative bg-gray-50 dark:bg-gray-700 rounded-lg p-4 overflow-x-auto">
        <svg width="750" height="150" className="min-w-full">
          {/* Renderizar aristas */}
          {edges.map((edge, index) => {
            const fromNode = nodes.find(n => n.id === edge.from)
            const toNode = nodes.find(n => n.id === edge.to)
            if (!fromNode || !toNode) return null

            return (
              <line
                key={index}
                x1={fromNode.x + 60}
                y1={fromNode.y + 15}
                x2={toNode.x}
                y2={toNode.y + 15}
                stroke="#6B7280"
                strokeWidth="2"
                markerEnd="url(#arrowhead)"
              />
            )
          })}

          {/* Definir marcador de flecha */}
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon
                points="0 0, 10 3.5, 0 7"
                fill="#6B7280"
              />
            </marker>
          </defs>

          {/* Renderizar nodos */}
          {nodes.map((node) => (
            <g key={node.id}>
              <rect
                x={node.x}
                y={node.y}
                width="120"
                height="30"
                rx="15"
                className={`${getStatusColor(node.status)} border-2`}
              />
              <foreignObject
                x={node.x + 5}
                y={node.y + 5}
                width="20"
                height="20"
              >
                {getStatusIcon(node.status)}
              </foreignObject>
              <text
                x={node.x + 30}
                y={node.y + 20}
                className="text-xs font-medium fill-current text-white"
                textAnchor="start"
              >
                {node.name.length > 12 ? node.name.substring(0, 12) + '...' : node.name}
              </text>
            </g>
          ))}
        </svg>
      </div>

      <div className="mt-4 flex justify-between items-center text-sm">
        <div className="flex space-x-4">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>Completado</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>En ejecución</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
            <span>Pendiente</span>
          </div>
        </div>
        <div className="text-gray-500">
          {nodes.filter(n => n.status === 'completed').length} / {nodes.length} completados
        </div>
      </div>
    </div>
  )
}

