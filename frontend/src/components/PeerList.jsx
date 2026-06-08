function PeerList({ peers, onSelectPeer, selectedPeer }) {
  if (peers.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        暂未发现其他节点
      </div>
    )
  }

  return (
    <ul className="space-y-3">
      {peers.map(peer => (
        <li 
          key={peer.id}
          className={`border rounded-lg p-4 cursor-pointer transition-colors ${
            selectedPeer === peer.id ? 'border-indigo-500 bg-indigo-50' : 'hover:border-gray-300'
          }`}
          onClick={() => onSelectPeer(peer.id)}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span className="font-medium">{peer.id.slice(0, 8)}...</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">IP: {peer.ip}</p>
            </div>
            
            <button
              onClick={(e) => {
                e.stopPropagation()
                onSelectPeer(peer.id)
              }}
              className="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700"
            >
              查看书单
            </button>
          </div>
        </li>
      ))}
    </ul>
  )
}

export default PeerList
