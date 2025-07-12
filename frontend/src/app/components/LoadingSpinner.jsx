export default function LoadingSpinner() {
  return (
    <div className="mt-6 text-center">
      <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
      <p className="mt-2 text-gray-500">Fetching recommendations...</p>
    </div>
  );
}
