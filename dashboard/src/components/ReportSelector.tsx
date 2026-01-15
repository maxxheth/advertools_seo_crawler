import React, { useState } from 'react';

function ReportSelector({ reports, selectedReport, onReportSelect, onRefresh }) {
  const [filter, setFilter] = useState('all');

  const filteredReports = filter === 'all' 
    ? reports 
    : reports.filter(r => r.crawler_type === filter);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-900">Reports</h2>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
        >
          Refresh
        </button>
      </div>

      <div className="mb-4">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded"
        >
          <option value="all">All Crawler Types</option>
          <option value="local_seo">Local SEO</option>
          <option value="general_seo">General SEO</option>
          <option value="technical_seo">Technical SEO</option>
          <option value="blogging">Blogging</option>
          <option value="ecommerce">E-commerce</option>
          <option value="news_media">News/Media</option>
          <option value="competitor">Competitor</option>
        </select>
      </div>

      {filteredReports.length > 0 ? (
        <div className="space-y-2">
          {filteredReports.map((report) => (
            <button
              key={report.id}
              onClick={() => onReportSelect(report)}
              className={`w-full text-left px-4 py-2 rounded border ${
                selectedReport?.id === report.id
                  ? 'bg-primary-100 border-primary-500'
                  : 'bg-white border-gray-200 hover:bg-gray-50'
              }`}
            >
              <div className="font-medium">{report.crawler_type}</div>
              <div className="text-sm text-gray-500">{report.timestamp}</div>
            </button>
          ))}
        </div>
      ) : (
        <p className="text-gray-500">No reports available</p>
      )}
    </div>
  );
}

export default ReportSelector;
