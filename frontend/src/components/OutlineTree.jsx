function OutlineTree({ outline }) {
  if (!outline) return null

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold">{outline.title}</h3>
        <p className="text-gray-600 mt-1">{outline.description}</p>
      </div>
      
      <div className="border-l-2 border-indigo-200 pl-4 space-y-3">
        {outline.chapters.map((chapter, index) => (
          <div key={index} className="relative">
            <div className="absolute -left-[22px] top-1 w-3 h-3 bg-indigo-500 rounded-full"></div>
            <div className="bg-gray-50 p-3 rounded-md">
              <h4 className="font-medium">第{index + 1}章：{chapter.title}</h4>
              <p className="text-sm text-gray-600 mt-1">{chapter.summary}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default OutlineTree
