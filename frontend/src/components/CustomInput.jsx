export default function CustomInput({ value, onChange, placeholder, disabled = false, type = 'text' }) {
  return (
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      className={`w-full px-3 py-2 border rounded-lg text-sm transition-all
        ${disabled 
          ? 'bg-gray-50 text-gray-400 border-gray-200 cursor-not-allowed' 
          : 'border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 hover:border-gray-400'}`}
    />
  )
}
