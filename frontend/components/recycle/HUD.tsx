'use client'

import { useState, useEffect } from 'react'

interface Project {
  id: string
  name: string
  progress: number
  phase: string
  eta: string
  quotas: {
    used: number
    remaining: number
  }
}

export function HUD() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simular carga de datos
    setTimeout(() => {
      setProjects([
        {
          id: '1',
          name: 'Análisis de Documentos Legales',
          progress: 75,
          phase: 'Procesamiento',
          eta: '2 horas',
          quotas: { used: 1250, remaining: 750 }
        },
        {
          id: '2',
          name: 'Extracción de Datos Financieros',
          progress: 45,
          phase: 'Análisis',
          eta: '4 horas',
          quotas: { used: 800, remaining: 1200 }
        }
      ])
      setLoading(false)
    }, 1000)
  }, [])

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Panel de Control</h2>
      <div className="space-y-4">
        {projects.map((project) => (
          <div key={project.id} className="border rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-medium">{project.name}</h3>
              <span className="text-sm text-gray-500">{project.eta}</span>
            </div>
            <div className="mb-2">
              <div className="flex justify-between text-sm mb-1">
                <span>Progreso</span>
                <span>{project.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${project.progress}%` }}
                ></div>
              </div>
            </div>
            <div className="flex justify-between text-sm text-gray-600">
              <span>Fase: {project.phase}</span>
              <span>Cuotas: {project.quotas.used}/{project.quotas.used + project.quotas.remaining}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

