import React from 'react';

function MetricsCard({ title, value }) {
  const formatValue = (val) => {
    if (typeof val === 'number') {
      return val.toFixed(2);
    }
    return val;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-sm font-medium text-gray-500 uppercase">{title}</h3>
      <p className="mt-2 text-2xl font-bold text-gray-900">
        {formatValue(value)}
      </p>
    </div>
  );
}

export default MetricsCard;
