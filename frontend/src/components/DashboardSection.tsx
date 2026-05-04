'use client';

import { motion } from 'framer-motion';
import { 
  Upload, X, File, Loader2, FileText, TrendingUp 
} from 'lucide-react';
import { 
  DashboardTile, 
  UploadedFile, 
  AnalysisData, 
  Contract, 
  RecentAnalysis, 
  Clause 
} from '@/models/models';
import { getDummyDashboardTiles } from '@/models/dummy';
import { getTilesFromAnalysis } from '@/models/dataFiller';
import SectionNavigation from './SectionNavigation';

interface CTA {
  action: string;
  data: any;
}

interface DashboardSectionProps {
  analysisResults: AnalysisData | null;
  
  getRiskLevel: (score: number) => string;
  
  // Recent Analyses
  recentAnalyses: RecentAnalysis[];
  isLoadingAnalyses: boolean;
  fetchRecentAnalysis: () => void;
  onDashboardAction?: (cta: CTA) => void;
  onHome?: () => void;
}

export default function DashboardSection({
  getRiskLevel,
  recentAnalyses,
  isLoadingAnalyses,
  fetchRecentAnalysis,
  onDashboardAction,
  onHome
}: DashboardSectionProps) {

  // Generate dynamic dashboard tiles based on analysis results
  const getDashboardTiles = (): DashboardTile[] => {
    // if (analysisResults) {
    //   return getTilesFromAnalysis(analysisResults);
    // }
    
    return getDummyDashboardTiles();
  };

  const handleTileClick = (section: string) => {
    console.log('Tile clicked:', section);
    onDashboardAction?.({ action: 'tile-click', data: { section } });
  };

  return (
    <div className="flex-1 overflow-y-auto">
      <SectionNavigation
        title="Dashboard Overview"
        subtitle="Monitor your contract intelligence metrics"
        showBackButton={false}
        showHomeButton={false}
        onHome={onHome}
      />
      
      <div className="max-w-6xl px-6 py-6">

   

        {/* Dashboard Tiles Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {getDashboardTiles().map((tile, index) => (
            <motion.div
              key={tile.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
              onClick={() => tile.onClick && handleTileClick(tile.onClick)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-lg ${tile.color}`}>
                  {tile.icon}
                </div>
                <span className="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded">
                  {tile.trend}
                </span>
              </div>
              <div className="mb-1">
                <h3 className="text-2xl font-semibold">{tile.value}</h3>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-900">{tile.title}</h4>
                <p className="text-xs text-gray-500">{tile.subtitle}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Recent Analyses Section */}
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-light">Recent Analyses</h2>
            <button
              onClick={fetchRecentAnalysis}
              disabled={isLoadingAnalyses}
              className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isLoadingAnalyses ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Loading...
                </>
              ) : (
                'Refresh'
              )}
            </button>
          </div>
          
          {isLoadingAnalyses ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
            </div>
          ) : recentAnalyses.length === 0 ? (
            <div className="text-center py-8">
              <TrendingUp className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No recent analyses found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {recentAnalyses.map((analysis) => (
                <motion.div
                  key={analysis.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{analysis.analysis.contract_name}</h3>
                      <p className="text-sm text-gray-500">
                        {new Date(analysis.analysis_date).toLocaleDateString()} at {new Date(analysis.analysis_date).toLocaleTimeString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        analysis.risk_level === 'high' ? 'bg-red-100 text-red-800' :
                        analysis.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {analysis.risk_level.charAt(0).toUpperCase() + analysis.risk_level.slice(1)} Risk
                      </span>
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                        Score: {analysis.overall_risk_score}
                      </span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">{analysis.legal_risk_score}</div>
                      <div className="text-xs text-gray-500">Legal Risk</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">{analysis.financial_risk_score}</div>
                      <div className="text-xs text-gray-500">Financial Risk</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">{analysis.operational_risk_score}</div>
                      <div className="text-xs text-gray-500">Operational Risk</div>
                    </div>
                  </div>
                  
                  {analysis.executive_summary && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Executive Summary</h4>
                      <p className="text-sm text-gray-600">{analysis.executive_summary}</p>
                    </div>
                  )}
                  
                  {analysis.key_recommendations && analysis.key_recommendations.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Key Recommendations</h4>
                      <ul className="space-y-1">
                        {analysis.key_recommendations.map((rec, index) => (
                          <li key={index} className="text-sm text-gray-600 flex items-start">
                            <span className="text-blue-500 mr-2">•</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </div>

        

        {/* Recent Activity Section */}
        <div className="mt-8">
          <h2 className="text-xl font-light mb-4">Recent Activity</h2>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Contract #1234 reviewed</p>
                  <p className="text-xs text-gray-500">2 hours ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">High-risk contract flagged</p>
                  <p className="text-xs text-gray-500">4 hours ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Compliance check completed</p>
                  <p className="text-xs text-gray-500">6 hours ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
