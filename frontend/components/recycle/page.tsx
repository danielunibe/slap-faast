import { HUD } from '@/components/HUD'
import { ClusterStrip } from '@/components/ClusterStrip'
import { TabBar } from '@/components/TabBar'
import { InspectorDrawer } from '@/components/InspectorDrawer'
import { MiniDAG } from '@/components/MiniDAG'

export default function Home() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <HUD />
        </div>
        <div>
          <ClusterStrip />
        </div>
      </div>
      
      <TabBar />
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <MiniDAG />
        </div>
        <div>
          <InspectorDrawer />
        </div>
      </div>
    </div>
  )
}

