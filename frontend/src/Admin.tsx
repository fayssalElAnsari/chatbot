import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import UserNav from './UserNav'
import { Button } from './components/ui/button'
import SideBar from "./SideBar"

const Admin = () => {

  return (
    <div>
      <div className="hidden flex-col md:flex">
        <div className="border-b">
          <div className="flex h-16 items-center justify-between px-4">
            <div className="ml-auto flex items-center space-x-4">
              <UserNav />
            </div>
          </div>
        </div>
      </div>


      <ResizablePanelGroup
        direction="horizontal"
        className="rounded-lg border md:min-w-[450px] mt-3"
      >
        <ResizablePanel defaultSize={15} className='w-[30%] h-full'>
          <div className="flex h-full items-center p-2 mr-auto">
            <SideBar />
          </div>
        </ResizablePanel>

        <ResizableHandle withHandle />
        <ResizablePanel>
          <div className="flex h-full items-center justify-center p-6">
            <Button className="font-semibold ml-auto">+ Ingest Document</Button>
            {/* <DataTable data={documents} columns={columns} /> */}
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>

    </div>

  )
}

export default Admin