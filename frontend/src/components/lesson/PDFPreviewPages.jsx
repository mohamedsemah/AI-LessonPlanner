// frontend/src/components/lesson/PDFPreviewPages.jsx

import React from 'react';
import { formatDuration, formatGradeLevel, cleanOverviewText, capitalize } from '../../utils/helpers';
import { BookOpen, Target, Clock, Users, FileText, CheckCircle, Settings, Zap } from 'lucide-react';

// Table of Contents Page
export const TableOfContentsPage = () => (
  <div className="w-full min-h-full p-16 bg-white page-content">
    {/* Header */}
    <div className="border-b-2 border-blue-600 pb-6 mb-12">
      <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-4">
        <BookOpen className="w-10 h-10 text-blue-600" />
        Table of Contents
      </h1>
    </div>

    {/* Contents */}
    <div className="space-y-4 text-lg">
      {[
        { title: 'Lesson Overview', page: 3, icon: '📋', description: 'Course information and lesson description' },
        { title: 'Learning Objectives', page: 4, icon: '🎯', description: 'Bloom\'s taxonomy-based objectives' },
        { title: 'Lesson Plan Details', page: 5, icon: '📚', description: 'Materials, prerequisites, and strategies' },
        { title: 'Gagne\'s Nine Events of Instruction', page: 6, icon: '⚡', description: 'Structured instructional framework' },
        { title: 'Appendices', page: 10, icon: '📎', description: 'Reference materials and guides' },
        { title: 'A. Bloom\'s Taxonomy Reference', page: 10, icon: '', indent: true, description: 'Cognitive levels and action verbs' },
        { title: 'B. Gagne\'s Events Reference', page: 11, icon: '', indent: true, description: 'Instructional design strategies' }
      ].map((item, index) => (
        <div
          key={index}
          className={`group py-4 border-b border-gray-100 hover:bg-gray-50 transition-colors rounded-lg px-2 ${
            item.indent ? 'ml-8' : ''
          }`}
        >
          <div className="flex justify-between items-start">
            <div className="flex items-start gap-4 flex-1">
              {item.icon && <span className="text-2xl">{item.icon}</span>}
              <div className="flex-1">
                <h3 className={`font-semibold ${item.indent ? 'text-base text-gray-700' : 'text-lg text-gray-900'}`}>
                  {item.title}
                </h3>
                {item.description && (
                  <p className="text-sm text-gray-500 mt-1">{item.description}</p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="hidden group-hover:block w-20 border-b border-dotted border-gray-300"></div>
              <span className="font-mono text-blue-600 font-bold bg-blue-50 px-2 py-1 rounded">
                {item.page}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>

    {/* Footer */}
    <div className="mt-12 pt-6 border-t border-gray-200">
      <div className="text-center text-sm text-gray-500">
        <p className="font-medium">This lesson plan follows evidence-based pedagogical principles</p>
        <p className="text-xs mt-1">Generated with AI assistance • Based on educational research</p>
      </div>
    </div>
  </div>
);

// Lesson Overview Page
export const LessonOverviewPage = ({ lessonData }) => (
  <div className="w-full min-h-full p-16 bg-white page-content">
    {/* Header */}
    <div className="border-b-2 border-green-600 pb-6 mb-10">
      <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-4">
        <FileText className="w-10 h-10 text-green-600" />
        Lesson Overview
      </h1>
      <p className="text-gray-600 mt-2 text-lg">Comprehensive lesson structure and design</p>
    </div>

    {/* Quick Stats Grid */}
    <div className="grid grid-cols-2 gap-6 mb-10">
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl border-l-4 border-blue-500 shadow-sm">
        <div className="flex items-center gap-3 mb-2">
          <Clock className="w-6 h-6 text-blue-600" />
          <span className="text-sm font-semibold text-blue-700 uppercase tracking-wide">Duration</span>
        </div>
        <p className="text-3xl font-bold text-blue-900">
          {formatDuration(lessonData.total_duration || lessonData.lesson_info?.duration_minutes)}
        </p>
      </div>

      <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl border-l-4 border-green-500 shadow-sm">
        <div className="flex items-center gap-3 mb-2">
          <Users className="w-6 h-6 text-green-600" />
          <span className="text-sm font-semibold text-green-700 uppercase tracking-wide">Grade Level</span>
        </div>
        <p className="text-3xl font-bold text-green-900">
          {formatGradeLevel(lessonData.lesson_info?.grade_level)}
        </p>
      </div>

      <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border-l-4 border-purple-500 shadow-sm">
        <div className="flex items-center gap-3 mb-2">
          <Target className="w-6 h-6 text-purple-600" />
          <span className="text-sm font-semibold text-purple-700 uppercase tracking-wide">Objectives</span>
        </div>
        <p className="text-3xl font-bold text-purple-900">
          {lessonData.objectives?.length || 0}
        </p>
      </div>

      <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl border-l-4 border-orange-500 shadow-sm">
        <div className="flex items-center gap-3 mb-2">
          <Zap className="w-6 h-6 text-orange-600" />
          <span className="text-sm font-semibold text-orange-700 uppercase tracking-wide">Events</span>
        </div>
        <p className="text-3xl font-bold text-orange-900">
          {lessonData.gagne_events?.length || 0}
        </p>
      </div>
    </div>

    {/* Course Information */}
    <div className="mb-10 p-8 bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl border border-gray-200 shadow-sm">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <BookOpen className="w-5 h-5 text-white" />
        </div>
        Course Information
      </h2>
      <div className="grid grid-cols-1 gap-6">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <span className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Course Title</span>
          <p className="text-xl font-bold text-gray-900 mt-1">{lessonData.lesson_info?.course_title}</p>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <span className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Lesson Topic</span>
          <p className="text-xl font-bold text-gray-900 mt-1">{lessonData.lesson_info?.lesson_topic}</p>
        </div>
      </div>
    </div>

    {/* Overview Description */}
    <div className="mb-10">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
        <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
          <FileText className="w-5 h-5 text-white" />
        </div>
        Lesson Description
      </h2>
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <div
          className="prose prose-lg max-w-none text-gray-700 leading-relaxed"
          dangerouslySetInnerHTML={{
            __html: cleanOverviewText(lessonData.lesson_plan?.overview || 'This lesson provides comprehensive coverage of the topic with engaging activities and assessments.')
          }}
        />
      </div>
    </div>

    {/* Cognitive Levels */}
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
        <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
          <Target className="w-5 h-5 text-white" />
        </div>
        Cognitive Levels Addressed
      </h2>
      <div className="flex flex-wrap gap-3">
        {[...new Set(lessonData.objectives?.map(obj => obj.bloom_level) || [])].map(level => (
          <span
            key={level}
            className={`px-6 py-3 rounded-lg text-sm font-bold shadow-sm ${getBloomColorClass(level)}`}
          >
            {capitalize(level)}
          </span>
        ))}
      </div>
    </div>
  </div>
);

// Learning Objectives Page
export const LearningObjectivesPage = ({ lessonData }) => {
  const objectivesByBloom = (lessonData.objectives || []).reduce((groups, obj) => {
    const level = obj.bloom_level;
    if (!groups[level]) groups[level] = [];
    groups[level].push(obj);
    return groups;
  }, {});

  return (
    <div className="w-full min-h-full p-16 bg-white page-content">
      {/* Header */}
      <div className="border-b-2 border-purple-600 pb-6 mb-10">
        <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-4">
          <Target className="w-10 h-10 text-purple-600" />
          Learning Objectives
        </h1>
        <p className="text-gray-600 mt-2 text-lg">
          Based on Bloom's Taxonomy • {lessonData.objectives?.length || 0} total objectives across {Object.keys(objectivesByBloom).length} cognitive levels
        </p>
      </div>

      {/* Objectives by Bloom Level */}
      <div className="space-y-8">
        {Object.entries(objectivesByBloom).map(([level, objectives]) => (
          <div key={level} className="border border-gray-200 rounded-xl overflow-hidden shadow-sm">
            {/* Level Header */}
            <div className={`p-6 ${getBloomBgClass(level)} border-b border-gray-200`}>
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-4">
                  <span className={`w-4 h-4 rounded-full ${getBloomDotClass(level)}`}></span>
                  {capitalize(level)} Level
                </h2>
                <span className="bg-white bg-opacity-90 px-4 py-2 rounded-full text-sm font-bold text-gray-700 shadow-sm">
                  {objectives.length} objective{objectives.length !== 1 ? 's' : ''}
                </span>
              </div>
              <p className="text-sm text-gray-600 mt-2 font-medium">{getBloomDescription(level)}</p>
            </div>

            {/* Objectives List */}
            <div className="p-6 space-y-4 bg-white">
              {objectives.map((objective, index) => (
                <div key={index} className="flex gap-4 p-5 bg-gray-50 rounded-lg border border-gray-200 hover:shadow-sm transition-shadow">
                  <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-blue-600">{index + 1}</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-gray-900 font-semibold leading-relaxed text-lg">{objective.objective}</p>
                    {objective.condition && (
                      <p className="text-sm text-gray-600 mt-2">
                        <span className="font-semibold">Condition:</span> {objective.condition}
                      </p>
                    )}
                    {objective.criteria && (
                      <p className="text-sm text-gray-600 mt-1">
                        <span className="font-semibold">Criteria:</span> {objective.criteria}
                      </p>
                    )}
                    <div className="flex items-center gap-6 mt-3 text-xs text-gray-500">
                      <span><span className="font-semibold">Action Verb:</span> {objective.action_verb}</span>
                      <span><span className="font-semibold">Content:</span> {objective.content}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Lesson Plan Page
export const LessonPlanPage = ({ lessonData }) => (
  <div className="w-full min-h-full p-16 bg-white page-content">
    {/* Header */}
    <div className="border-b-2 border-blue-600 pb-6 mb-10">
      <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-4">
        <BookOpen className="w-10 h-10 text-blue-600" />
        Lesson Plan Details
      </h1>
      <p className="text-gray-600 mt-2 text-lg">Comprehensive planning framework and resources</p>
    </div>

    {/* Plan Sections */}
    <div className="space-y-8">
      {/* Prerequisites */}
      {lessonData.lesson_plan?.prerequisites?.length > 0 && (
        <div className="border border-gray-200 rounded-xl p-8 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
            Prerequisites
          </h2>
          <ul className="space-y-3">
            {lessonData.lesson_plan.prerequisites.map((prereq, index) => (
              <li key={index} className="flex items-start gap-4 text-gray-700 p-3 bg-green-50 rounded-lg">
                <span className="w-3 h-3 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></span>
                <span className="font-medium">{prereq}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Materials */}
      {lessonData.lesson_plan?.materials?.length > 0 && (
        <div className="border border-gray-200 rounded-xl p-8 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <BookOpen className="w-6 h-6 text-blue-600" />
            Materials and Resources
          </h2>
          <div className="grid grid-cols-2 gap-4">
            {lessonData.lesson_plan.materials.map((material, index) => (
              <div key={index} className="flex items-center gap-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-gray-700 font-medium">{material}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Technology Requirements */}
      {lessonData.lesson_plan?.technology_requirements?.length > 0 && (
        <div className="border border-gray-200 rounded-xl p-8 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Settings className="w-6 h-6 text-purple-600" />
            Technology Requirements
          </h2>
          <div className="grid grid-cols-2 gap-4">
            {lessonData.lesson_plan.technology_requirements.map((tech, index) => (
              <div key={index} className="flex items-center gap-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span className="text-gray-700 font-medium">{tech}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Assessment Methods */}
      {lessonData.lesson_plan?.assessment_methods?.length > 0 && (
        <div className="border border-gray-200 rounded-xl p-8 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Target className="w-6 h-6 text-orange-600" />
            Assessment Methods
          </h2>
          <div className="grid grid-cols-1 gap-4">
            {lessonData.lesson_plan.assessment_methods.map((method, index) => (
              <div key={index} className="flex items-center gap-4 p-4 bg-orange-50 rounded-lg border border-orange-200">
                <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                <span className="text-gray-700 font-medium">{method}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Differentiation Strategies */}
      {lessonData.lesson_plan?.differentiation_strategies?.length > 0 && (
        <div className="border border-gray-200 rounded-xl p-8 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Users className="w-6 h-6 text-green-600" />
            Differentiation Strategies
          </h2>
          <div className="grid grid-cols-1 gap-4">
            {lessonData.lesson_plan.differentiation_strategies.map((strategy, index) => (
              <div key={index} className="flex items-center gap-4 p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-gray-700 font-medium">{strategy}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Closure Activities */}
      {lessonData.lesson_plan?.closure_activities?.length > 0 && (
        <div className="border border-gray-200 rounded-xl p-8 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <CheckCircle className="w-6 h-6 text-indigo-600" />
            Closure Activities
          </h2>
          <div className="grid grid-cols-1 gap-4">
            {lessonData.lesson_plan.closure_activities.map((activity, index) => (
              <div key={index} className="flex items-center gap-4 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                <div className="w-3 h-3 bg-indigo-500 rounded-full"></div>
                <span className="text-gray-700 font-medium">{activity}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  </div>
);

// Gagne Events Page
export const GagneEventsPage = ({ events, pageNumber, totalGagnePages }) => (
  <div className="w-full min-h-full p-16 bg-white page-content">
    {/* Header */}
    <div className="border-b-2 border-indigo-600 pb-6 mb-10">
      <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-4">
        <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-lg">G</span>
        </div>
        Gagne's Nine Events of Instruction
      </h1>
      <p className="text-gray-600 mt-2 text-lg">
        Page {pageNumber} of {totalGagnePages} • Evidence-based instructional design framework
      </p>
    </div>

    {/* Events */}
    <div className="space-y-10">
      {events.map((event, index) => (
        <div key={event.event_number} className="border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          {/* Event Header */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-8 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-6">
                <div className="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold text-2xl">{event.event_number}</span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{event.event_name}</h2>
                  <p className="text-gray-600 mt-1 font-medium">{event.description}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="bg-white px-4 py-2 rounded-full border-2 border-indigo-200 shadow-sm">
                  <span className="text-lg font-bold text-indigo-700">
                    {formatDuration(event.duration_minutes)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Event Content */}
          <div className="p-8 bg-white space-y-6">
            {/* Activities */}
            {event.activities?.length > 0 && (
              <div>
                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-3 text-lg">
                  <div className="w-5 h-5 bg-blue-500 rounded"></div>
                  Activities
                </h3>
                <div className="space-y-3">
                  {event.activities.map((activity, actIndex) => (
                    <div key={actIndex} className="flex items-start gap-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <span className="text-blue-600 font-bold text-lg mt-0.5 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        {actIndex + 1}
                      </span>
                      <span className="text-gray-700 font-medium leading-relaxed">{activity}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Materials */}
            {event.materials_needed?.length > 0 && (
              <div>
                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-3 text-lg">
                  <div className="w-5 h-5 bg-green-500 rounded"></div>
                  Materials Needed
                </h3>
                <div className="flex flex-wrap gap-3">
                  {event.materials_needed.map((material, matIndex) => (
                    <span
                      key={matIndex}
                      className="px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm font-bold border border-green-200"
                    >
                      {material}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Assessment Strategy */}
            {event.assessment_strategy && (
              <div>
                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-3 text-lg">
                  <div className="w-5 h-5 bg-orange-500 rounded"></div>
                  Assessment Strategy
                </h3>
                <p className="text-gray-700 p-4 bg-orange-50 rounded-lg font-medium border border-orange-200">
                  {event.assessment_strategy}
                </p>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Bloom's Taxonomy Appendix
export const BloomAppendixPage = () => (
  <div className="w-full min-h-full p-16 bg-white page-content">
    {/* Header */}
    <div className="border-b-2 border-red-600 pb-6 mb-10">
      <h1 className="text-4xl font-bold text-gray-900">
        Appendix A: Bloom's Taxonomy Reference
      </h1>
      <p className="text-gray-600 mt-2 text-lg">Cognitive levels and associated action verbs</p>
    </div>

    {/* Bloom's Levels */}
    <div className="space-y-6">
      {[
        {
          level: 'Remember',
          description: 'Recall facts and basic concepts',
          verbs: ['define', 'duplicate', 'list', 'memorize', 'recall', 'repeat', 'state'],
          color: 'red'
        },
        {
          level: 'Understand',
          description: 'Explain ideas or concepts',
          verbs: ['classify', 'describe', 'discuss', 'explain', 'identify', 'locate', 'recognize', 'report'],
          color: 'orange'
        },
        {
          level: 'Apply',
          description: 'Use information in new situations',
          verbs: ['execute', 'implement', 'solve', 'use', 'demonstrate', 'interpret', 'operate', 'schedule'],
          color: 'yellow'
        },
        {
          level: 'Analyze',
          description: 'Draw connections among ideas',
          verbs: ['differentiate', 'organize', 'relate', 'compare', 'contrast', 'distinguish', 'examine', 'experiment'],
          color: 'green'
        },
        {
          level: 'Evaluate',
          description: 'Justify a stand or decision',
          verbs: ['appraise', 'argue', 'defend', 'judge', 'select', 'support', 'value', 'critique'],
          color: 'blue'
        },
        {
          level: 'Create',
          description: 'Produce new or original work',
          verbs: ['design', 'assemble', 'construct', 'conjecture', 'develop', 'formulate', 'author', 'investigate'],
          color: 'purple'
        }
      ].map((item, index) => (
        <div key={index} className={`border-2 border-${item.color}-200 rounded-xl overflow-hidden shadow-sm`}>
          <div className={`bg-${item.color}-50 p-6 border-b border-${item.color}-200`}>
            <h2 className="text-2xl font-bold text-gray-900">{item.level}</h2>
            <p className="text-gray-600 font-medium mt-1">{item.description}</p>
          </div>
          <div className="p-6 bg-white">
            <h3 className="font-bold text-gray-900 mb-3">Key Action Verbs:</h3>
            <div className="flex flex-wrap gap-2">
              {item.verbs.map((verb, verbIndex) => (
                <span
                  key={verbIndex}
                  className={`px-3 py-2 bg-${item.color}-100 text-${item.color}-800 rounded-full text-sm font-semibold border border-${item.color}-200`}
                >
                  {verb}
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Gagne's Events Appendix
export const GagneAppendixPage = () => (
  <div className="w-full min-h-full p-16 bg-white page-content">
    {/* Header */}
    <div className="border-b-2 border-indigo-600 pb-6 mb-10">
      <h1 className="text-4xl font-bold text-gray-900">
        Appendix B: Gagne's Nine Events Quick Reference
      </h1>
    </div>

    {/* Events Reference */}
    <div className="space-y-5">
      {[
        { number: 1, name: 'Gain Attention', purpose: 'Capture student interest', strategies: ['Question', 'story', 'demonstration', 'multimedia'] },
        { number: 2, name: 'Inform Objectives', purpose: 'Share learning goals', strategies: ['Present objectives', 'explain relevance'] },
        { number: 3, name: 'Stimulate Recall', purpose: 'Connect to prior knowledge', strategies: ['Review', 'prerequisites', 'bridging'] },
        { number: 4, name: 'Present Content', purpose: 'Deliver new information', strategies: ['Lecture', 'reading', 'multimedia', 'examples'] },
        { number: 5, name: 'Provide Guidance', purpose: 'Guide learning process', strategies: ['Coaching', 'hints', 'prompts', 'modeling'] },
        { number: 6, name: 'Elicit Performance', purpose: 'Students practice', strategies: ['Exercises', 'problems', 'simulations'] },
        { number: 7, name: 'Provide Feedback', purpose: 'Give constructive feedback', strategies: ['Corrections', 'explanations', 'reinforcement'] },
        { number: 8, name: 'Assess Performance', purpose: 'Evaluate learning', strategies: ['Tests', 'observations', 'portfolios'] },
        { number: 9, name: 'Enhance Retention', purpose: 'Promote transfer', strategies: ['Summary', 'real-world applications', 'reflection'] }
      ].map((event, index) => (
        <div key={index} className="flex items-center gap-8 p-6 border-2 border-gray-200 rounded-lg bg-gradient-to-r from-gray-50 to-indigo-50 shadow-sm">
          <div className="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
            <span className="text-white font-bold text-xl">{event.number}</span>
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-gray-900 text-lg">{event.name}</h3>
            <p className="text-gray-600 mb-3 font-medium">{event.purpose}</p>
            <div className="flex flex-wrap gap-2">
              {event.strategies.map((strategy, stratIndex) => (
                <span key={stratIndex} className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded text-sm font-semibold border border-indigo-200">
                  {strategy}
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Helper functions
const getBloomColorClass = (level) => {
  const colorMap = {
    remember: 'bg-red-100 text-red-800 border-red-200',
    understand: 'bg-orange-100 text-orange-800 border-orange-200',
    apply: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    analyze: 'bg-green-100 text-green-800 border-green-200',
    evaluate: 'bg-blue-100 text-blue-800 border-blue-200',
    create: 'bg-purple-100 text-purple-800 border-purple-200'
  };
  return colorMap[level] || 'bg-gray-100 text-gray-800 border-gray-200';
};

const getBloomBgClass = (level) => {
  const colorMap = {
    remember: 'bg-red-50',
    understand: 'bg-orange-50',
    apply: 'bg-yellow-50',
    analyze: 'bg-green-50',
    evaluate: 'bg-blue-50',
    create: 'bg-purple-50'
  };
  return colorMap[level] || 'bg-gray-50';
};

const getBloomDotClass = (level) => {
  const colorMap = {
    remember: 'bg-red-500',
    understand: 'bg-orange-500',
    apply: 'bg-yellow-500',
    analyze: 'bg-green-500',
    evaluate: 'bg-blue-500',
    create: 'bg-purple-500'
  };
  return colorMap[level] || 'bg-gray-500';
};

const getBloomDescription = (level) => {
  const descriptions = {
    remember: 'Recall facts, basic concepts, and answers',
    understand: 'Explain ideas or concepts and interpret information',
    apply: 'Use information in new situations and solve problems',
    analyze: 'Draw connections and distinguish between different parts',
    evaluate: 'Justify decisions and critique work or ideas',
    create: 'Produce new or original work and combine ideas'
  };
  return descriptions[level] || 'Learning objective';
};