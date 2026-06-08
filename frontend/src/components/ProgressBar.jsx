function ProgressBar({ current, total }) {
  const percentage = total > 0 ? (current / total) * 100 : 0

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm text-gray-600">
        <span>章节进度</span>
        <span>{current} / {total}</span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div 
          className="bg-indigo-600 h-full transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
      
      <div className="text-center text-sm font-medium text-indigo-600">
        {Math.round(percentage)}% 完成
      </div>
    </div>
  )
}

export default ProgressBar
