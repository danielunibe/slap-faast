'use client'

import { useState } from 'react'

const tabs = [
  { id: 'projects', label: 'Proyectos', count: 5 },
  { id: 'tasks', label: 'Tareas', count: 12 },
  { id: 'queue', label: 'Cola', count: 8 },
  { id: 'completed', label: 'Completados', count: 23 },
  { id: 'errors', label: 'Errores', count: 2 }
]

export function TabBar() {
  const [activeTab, setActiveTab] = useState('projects')

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex space-x-8 px-6" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              {tab.label}
              <span className={`
                ml-2 py-0.5 px-2 rounded-full text-xs
                ${activeTab === tab.id
                  ? 'bg-blue-100 text-blue-600'
                  : 'bg-gray-100 text-gray-900'
                }
              `}>
                {tab.count}
              </span>
            </button>
          ))}
        </nav>
      </div>
      
      <div className="p-6">
        <div className="text-center text-gray-500">
          Contenido de la pestaña "{tabs.find(t => t.id === activeTab)?.label}"
          <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <p className="text-sm">
              Aquí se mostraría el contenido específico de cada pestaña.
              Actualmente mostrando: <strong>{activeTab}</strong>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

