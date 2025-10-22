// frontend/app/components/DataTable.js
'use client';

export default function DataTable({ title, data }) {
  if (!data || data.length === 0) {
    return <p className="text-gray-400">没有可显示的数据。</p>;
  }

  // 获取表头
  const headers = Object.keys(data[0]);

  return (
    <div className="space-y-4">
      <h4 className="font-semibold text-white">{title}</h4>
      <div className="overflow-x-auto rounded-lg border border-gray-700">
        <table className="min-w-full divide-y divide-gray-700">
          <thead className="bg-gray-800">
            <tr>
              {headers.map((header) => (
                <th key={header} scope="col" className="py-3.5 px-4 text-left text-sm font-semibold text-white">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700 bg-gray-900">
            {data.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {headers.map((header) => (
                  <td key={header} className="whitespace-nowrap px-4 py-4 text-sm text-gray-300">
                    {typeof row[header] === 'number' ? row[header].toFixed(2) : row[header]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}