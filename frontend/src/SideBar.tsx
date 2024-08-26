import {
    AlertCircle,
    Archive,
    ArchiveX,
    File,
    Inbox,
    MessagesSquare,
    Search,
    Send,
    ShoppingCart,
    Trash2,
    Users2,
    Settings
} from "lucide-react"
import { Nav } from "./Nav"
import Admin from "./Admin"
import { Route } from "react-router-dom"

const SideBar = () => {
    const isCollapsed = false

    return (
        <div>
            <Nav
                isCollapsed={isCollapsed}
                links={[
                    {
                        title: "Settings",
                        icon: Settings,
                        variant: "default",
                    },
                    {
                        title: "Documents",
                        icon: File,
                        variant: "ghost",
                    }
                ]}
            />
        </div>
    )
}

export default SideBar