import React from 'react';

interface MetricsCardProps {
  title: string;
  value: number | string;
}

function MetricsCard({ title, value }: MetricsCardProps): JSX.Element {
  const formatValue = (val: number | string): string => {
    if (typeof val === 'number') {
      return val.toFixed(2);
    }
    return String(val);
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
