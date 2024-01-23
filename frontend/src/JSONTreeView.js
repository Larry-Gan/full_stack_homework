import * as React from 'react'
import PropTypes from 'prop-types'
import Box from '@mui/material/Box'
import { TreeView } from '@mui/x-tree-view/TreeView'
import { TreeItem } from '@mui/x-tree-view/TreeItem'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import axios from 'axios'

function createTreeItem (node, nodeId, handleFileClick) {
  const isLeaf = (key) => ['Form', 'CAD', 'Scan'].includes(key)

  return (
      <TreeItem key={nodeId} nodeId={nodeId} label={nodeId.split('/').pop()}>
        {Object.keys(node).map((childId) => {
          const newId = `${nodeId}/${childId}`
          const childNode = node[childId]

          // Handles the leaves at the end of the json
          if (isLeaf(childId) && Array.isArray(childNode)) {
            return (
              <TreeItem key={newId} nodeId={newId} label={childId}>
                {childNode.map((item) => (
                  <TreeItem
                    key={item.uuid}
                    nodeId={item.uuid}
                    label={item.name}
                    onClick={() => handleFileClick(item)}
                  />
                ))}
              </TreeItem>
            )
          }

          // Recursively create tree
          if (childNode instanceof Object && !(childNode instanceof Array)) {
            return createTreeItem(childNode, newId, handleFileClick)
          }

          // Return branch
          return <TreeItem key={newId} nodeId={newId} label={childId} />
        })}
      </TreeItem>
  )
}

function JSONTreeView ({ setSelectedFile, setFileContent, selectedFile }) {
  const [jsonData, setJsonData] = React.useState(null)

  // Get file data from backend
  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/directory')
        setJsonData(response.data)
      } catch (error) {
        console.error('Error fetching data: ', error)
      }
    }

    fetchData()
  }, [])

  // Handle clicking on the leaves
  const handleFileClick = (node) => {
    if (!selectedFile || node.uuid !== selectedFile.uuid) {
      setSelectedFile(node)
      setFileContent('')
    }
  }

  const renderTree = (nodes) => (
    Object.keys(nodes).map((nodeId) => {
      const rootId = `/${nodeId}`
      if (nodes[nodeId] instanceof Object && !(nodes[nodeId] instanceof Array)) {
        return createTreeItem(nodes[nodeId], rootId, handleFileClick)
      } else {
        // Just in case
        return <TreeItem key={rootId} nodeId={rootId} label={nodeId} />
      }
    })
  )

  // If there's no data, display this instead of the tree
  if (!jsonData) {
    return <div>Loading...</div>
  }

  return (
        <div className="JSONTreeView">
            <h2>Customers</h2>
            <Box sx={{ height: '100vh', flexGrow: 1, maxWidth: 400, overflowY: 'auto' }}>
                <TreeView
                aria-label="rich object"
                defaultCollapseIcon={<ExpandMoreIcon />}
                defaultExpandIcon={<ChevronRightIcon />}
                defaultExpanded={['/']}
                >
                {renderTree(jsonData)}
                </TreeView>
            </Box>
        </div>
  )
}

// Define the prop types
JSONTreeView.propTypes = {
  setSelectedFile: PropTypes.func.isRequired,
  setFileContent: PropTypes.func.isRequired,
  selectedFile: PropTypes.shape({
    uuid: PropTypes.string,
    name: PropTypes.string,
    location: PropTypes.string
  })
}

export default JSONTreeView
