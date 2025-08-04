import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, TrendingUp, Brain, Users, Eye } from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';

const UDLComplianceReport = ({ compliance, recommendations }) => {
  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreIcon = (score) => {
    if (score >= 0.8) return <CheckCircle className="w-5 h-5 text-green-600" />;
    if (score >= 0.6) return <AlertCircle className="w-5 h-5 text-yellow-600" />;
    return <AlertCircle className="w-5 h-5 text-red-600" />;
  };

  const principles = [
    {
      name: 'Representation',
      description: 'Multiple means of presenting information',
      score: compliance.representation_score,
      icon: <Eye className="w-5 h-5" />,
      color: 'bg-blue-50 text-blue-700'
    },
    {
      name: 'Action & Expression',
      description: 'Multiple ways for students to respond',
      score: compliance.action_expression_score,
      icon: <Users className="w-5 h-5" />,
      color: 'bg-green-50 text-green-700'
    },
    {
      name: 'Engagement',
      description: 'Multiple ways to motivate learners',
      score: compliance.engagement_score,
      icon: <Brain className="w-5 h-5" />,
      color: 'bg-purple-50 text-purple-700'
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary-600" />
          UDL Compliance Report
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Score */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center p-6 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg"
        >
          <div className="flex items-center justify-center gap-3 mb-2">
            {getScoreIcon(compliance.overall_compliance)}
            <h3 className="text-xl font-bold text-gray-900">Overall UDL Compliance</h3>
          </div>
          <div className={`text-4xl font-bold ${getScoreColor(compliance.overall_compliance)}`}>
            {Math.round(compliance.overall_compliance * 100)}%
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {compliance.overall_compliance >= 0.8 
              ? 'Excellent UDL implementation'
              : compliance.overall_compliance >= 0.6
              ? 'Good UDL implementation with room for improvement'
              : 'Needs improvement in UDL implementation'
            }
          </p>
        </motion.div>

        {/* Individual Principles */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {principles.map((principle, index) => (
            <motion.div
              key={principle.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg ${principle.color}`}
            >
              <div className="flex items-center gap-2 mb-2">
                {principle.icon}
                <h4 className="font-semibold">{principle.name}</h4>
              </div>
              <p className="text-sm mb-3 opacity-80">{principle.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">
                  {Math.round(principle.score * 100)}%
                </span>
                {getScoreIcon(principle.score)}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="border-t pt-6"
          >
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-yellow-600" />
              Recommendations for Improvement
            </h4>
            <ul className="space-y-2">
              {recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></span>
                  {recommendation}
                </li>
              ))}
            </ul>
          </motion.div>
        )}

        {/* Missing Guidelines */}
        {compliance.missing_guidelines && compliance.missing_guidelines.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="border-t pt-6"
          >
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              Missing UDL Guidelines
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {compliance.missing_guidelines.map((guideline, index) => (
                <div key={index} className="flex items-center gap-2 text-sm text-gray-600">
                  <span className="w-1.5 h-1.5 bg-red-500 rounded-full"></span>
                  {guideline}
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </CardContent>
    </Card>
  );
};

export default UDLComplianceReport; 