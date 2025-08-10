import React from 'react';
import {
  UserGroupIcon,
  BuildingOfficeIcon,
  BriefcaseIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  TrophyIcon,
  ClockIcon,
  CalendarIcon,
  CubeIcon
} from '@heroicons/react/24/outline';

const iconMap = {
  users: UserGroupIcon,
  'user-group': UserGroupIcon,
  building: BuildingOfficeIcon,
  briefcase: BriefcaseIcon,
  'currency-dollar': CurrencyDollarIcon,
  'trending-up': ArrowTrendingUpIcon,
  trophy: TrophyIcon,
  clock: ClockIcon,
  calendar: CalendarIcon,
  cube: CubeIcon
};

const colorMap = {
  blue: {
    bg: 'bg-blue-50',
    text: 'text-blue-600',
    border: 'border-blue-200'
  },
  green: {
    bg: 'bg-green-50',
    text: 'text-green-600',
    border: 'border-green-200'
  },
  purple: {
    bg: 'bg-purple-50',
    text: 'text-purple-600',
    border: 'border-purple-200'
  },
  yellow: {
    bg: 'bg-yellow-50',
    text: 'text-yellow-600',
    border: 'border-yellow-200'
  },
  orange: {
    bg: 'bg-orange-50',
    text: 'text-orange-600',
    border: 'border-orange-200'
  },
  red: {
    bg: 'bg-red-50',
    text: 'text-red-600',
    border: 'border-red-200'
  },
  indigo: {
    bg: 'bg-indigo-50',
    text: 'text-indigo-600',
    border: 'border-indigo-200'
  }
};

const MetricCard = ({ title, value, subtitle, icon, color = 'blue', size = 'normal', trend, onClick }) => {
  const IconComponent = iconMap[icon] || CubeIcon;
  const colors = colorMap[color] || colorMap.blue;
  const isLarge = size === 'large';

  return (
    <div 
      className={`bg-white rounded-lg shadow-sm border ${colors.border} p-6 hover:shadow-md transition-shadow ${
        onClick ? 'cursor-pointer' : ''
      }`}
      onClick={onClick}
    >
      <div className="flex items-center">
        <div className={`flex-shrink-0 ${colors.bg} rounded-lg p-3`}>
          <IconComponent className={`${colors.text} ${isLarge ? 'h-8 w-8' : 'h-6 w-6'}`} />
        </div>
        
        <div className="ml-4 flex-1">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-gray-600 truncate">{title}</p>
            {trend && (
              <span className={`text-xs px-2 py-1 rounded-full ${
                trend > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {trend > 0 ? '+' : ''}{trend}%
              </span>
            )}
          </div>
          
          <p className={`${isLarge ? 'text-3xl' : 'text-2xl'} font-bold text-gray-900 mt-1`}>
            {value}
          </p>
          
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default MetricCard;