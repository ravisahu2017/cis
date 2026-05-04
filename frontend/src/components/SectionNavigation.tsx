'use client';

import { ArrowLeft, Home, Upload, FileText, BarChart3 } from 'lucide-react';

interface SectionNavigationProps {
  title: string;
  subtitle?: string;
  showBackButton?: boolean;
  showHomeButton?: boolean;
  onBack?: () => void;
  onHome?: () => void;
  extraActions?: React.ReactNode;
}

export default function SectionNavigation({ 
  title, 
  subtitle, 
  showBackButton = false, 
  showHomeButton = true,
  onBack, 
  onHome,
  extraActions 
}: SectionNavigationProps) {
  return (
    <div className="bg-white border-b border-gray-200">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Back Button */}
            {showBackButton && (
              <button
                onClick={onBack}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Go back"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
            )}
            
            {/* Home Button */}
            {showHomeButton && (
              <button
                onClick={onHome}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Go to dashboard"
              >
                <Home className="w-5 h-5 text-gray-600" />
              </button>
            )}
            
            {/* Section Title */}
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
              {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
            </div>
          </div>
          
          {/* Extra Actions */}
          {extraActions && (
            <div className="flex items-center space-x-3">
              {extraActions}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
