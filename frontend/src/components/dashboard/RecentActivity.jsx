import React from 'react';

const RecentActivity = ({ activities = [] }) => {
  const defaultActivities = [
    {
      id: 1,
      type: 'lead',
      title: 'New lead created',
      description: 'Enterprise CRM Implementation from TechCorp',
      timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
      user: 'John Doe',
      status: 'new'
    },
    {
      id: 2,
      type: 'opportunity',
      title: 'Opportunity updated',
      description: 'Cloud Migration Project moved to L2 stage',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      user: 'Jane Smith',
      status: 'updated'
    },
    {
      id: 3,
      type: 'quotation',
      title: 'Quotation sent',
      description: 'Q-2024-001 sent to DataFlow Inc',
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
      user: 'Mike Johnson',
      status: 'sent'
    },
    {
      id: 4,
      type: 'lead',
      title: 'Lead converted',
      description: 'Manufacturing Solutions lead converted to opportunity',
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
      user: 'Sarah Wilson',
      status: 'converted'
    }
  ];

  const displayActivities = activities.length > 0 ? activities : defaultActivities;

  const getActivityIcon = (type, status) => {
    const iconClass = "w-4 h-4";
    
    if (type === 'lead') {
      return (
        <svg className={`${iconClass} text-blue-600`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      );
    }
    
    if (type === 'opportunity') {
      return (
        <svg className={`${iconClass} text-green-600`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      );
    }
    
    if (type === 'quotation') {
      return (
        <svg className={`${iconClass} text-purple-600`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      );
    }
    
    return (
      <svg className={`${iconClass} text-gray-600`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    );
  };

  const getStatusColor = (status) => {
    const colors = {
      'new': 'text-blue-600',
      'updated': 'text-yellow-600',
      'sent': 'text-purple-600',
      'converted': 'text-green-600',
      'completed': 'text-green-600',
      'pending': 'text-orange-600',
      'cancelled': 'text-red-600'
    };
    return colors[status] || 'text-gray-600';
  };

  const formatTimestamp = (timestamp) => {
    const now = new Date();
    const diffMs = now - new Date(timestamp);
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 60) {
      return `${diffMins} minutes ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hours ago`;
    } else {
      return `${diffDays} days ago`;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
      
      <div className="space-y-4">
        {displayActivities.map((activity, index) => (
          <div key={activity.id || index} className="flex items-start space-x-3">
            {/* Icon */}
            <div className="flex-shrink-0 p-2 bg-gray-50 rounded-full">
              {getActivityIcon(activity.type, activity.status)}
            </div>
            
            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium text-gray-900 truncate">
                  {activity.title}
                </h4>
                <span className="text-xs text-gray-500 flex-shrink-0 ml-2">
                  {formatTimestamp(activity.timestamp)}
                </span>
              </div>
              
              <p className="text-sm text-gray-600 mt-1 truncate">
                {activity.description}
              </p>
              
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs text-gray-500">
                  by {activity.user}
                </span>
                <span className={`text-xs font-medium ${getStatusColor(activity.status)}`}>
                  {activity.status}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {displayActivities.length === 0 && (
        <div className="text-center py-8">
          <svg className="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p className="text-gray-500">No recent activity</p>
        </div>
      )}
      
      {/* View All Link */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
          View all activity →
        </button>
      </div>
    </div>
  );
};

export default RecentActivity;