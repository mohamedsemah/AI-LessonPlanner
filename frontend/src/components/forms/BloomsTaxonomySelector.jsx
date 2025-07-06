import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { cn } from '../../utils/helpers';
import Badge from '../ui/Badge';
import { BLOOM_LEVELS } from '../../utils/constants';

const BloomsTaxonomySelector = ({ selectedLevels, onChange, error }) => {
  const handleLevelToggle = (level) => {
    const isSelected = selectedLevels.includes(level);

    if (isSelected) {
      onChange(selectedLevels.filter(l => l !== level));
    } else {
      onChange([...selectedLevels, level]);
    }
  };

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        <p className="text-sm text-gray-600">
          Select the Bloom's taxonomy levels you want to include in your lesson objectives:
        </p>

        {error && (
          <motion.p
            className="text-sm text-red-600"
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {error}
          </motion.p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {BLOOM_LEVELS.map((level, index) => {
          const isSelected = selectedLevels.includes(level.value);

          return (
            <motion.div
              key={level.value}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <motion.button
                type="button"
                onClick={() => handleLevelToggle(level.value)}
                className={cn(
                  'w-full p-4 rounded-lg border-2 text-left transition-all duration-200 group relative overflow-hidden',
                  isSelected
                    ? 'border-primary-500 bg-primary-50 shadow-sm'
                    : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                )}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {/* Selection indicator */}
                <div className={cn(
                  'absolute top-3 right-3 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-200',
                  isSelected
                    ? 'border-primary-500 bg-primary-500'
                    : 'border-gray-300 group-hover:border-gray-400'
                )}>
                  {isSelected && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.2 }}
                    >
                      <Check className="w-4 h-4 text-white" />
                    </motion.div>
                  )}
                </div>

                {/* Content */}
                <div className="pr-8">
                  <div className="flex items-center gap-3 mb-2">
                    <Badge variant={level.value} size="sm">
                      {level.label}
                    </Badge>
                  </div>

                  <p className="text-sm text-gray-600 mb-3">
                    {level.description}
                  </p>

                  <div className="flex flex-wrap gap-1">
                    {level.verbs.slice(0, 3).map((verb, verbIndex) => (
                      <span
                        key={verb}
                        className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                      >
                        {verb}
                      </span>
                    ))}
                    {level.verbs.length > 3 && (
                      <span className="text-xs text-gray-400 px-2 py-1">
                        +{level.verbs.length - 3} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Hover effect */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-primary-500/0 to-primary-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                  initial={false}
                />
              </motion.button>
            </motion.div>
          );
        })}
      </div>

      {/* Selection summary */}
      {selectedLevels.length > 0 && (
        <motion.div
          className="mt-4 p-4 bg-gray-50 rounded-lg"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
        >
          <p className="text-sm font-medium text-gray-700 mb-2">
            Selected levels ({selectedLevels.length}):
          </p>
          <div className="flex flex-wrap gap-2">
            {selectedLevels.map(level => {
              const bloomLevel = BLOOM_LEVELS.find(l => l.value === level);
              return (
                <Badge key={level} variant={level} size="sm">
                  {bloomLevel?.label}
                </Badge>
              );
            })}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default BloomsTaxonomySelector;