// utils/timeRedistribution.js
// Smart Time Redistribution Strategies for Gagne Events

import { formatDuration } from './helpers';

/**
 * Strategy 1: Proportional Redistribution
 * Distribute time changes proportionally across other events based on their original weights
 */
export function redistributeProportionally(events, targetTotalDuration) {
  const currentTotal = events.reduce((sum, event) => sum + event.duration_minutes, 0);
  const timeDifference = targetTotalDuration - currentTotal;

  if (Math.abs(timeDifference) <= 1) return events; // No significant change needed

  console.log(`📊 Proportional redistribution: ${timeDifference > 0 ? 'adding' : 'removing'} ${Math.abs(timeDifference)} minutes`);

  // Calculate total weight of all events (excluding minimum 1 minute per event)
  const totalFlexibleTime = currentTotal - events.length; // Reserve 1 min per event

  return events.map(event => {
    const eventFlexibleTime = Math.max(0, event.duration_minutes - 1);
    const weight = totalFlexibleTime > 0 ? eventFlexibleTime / totalFlexibleTime : 1 / events.length;
    const adjustment = Math.round(timeDifference * weight);
    const newDuration = Math.max(1, event.duration_minutes + adjustment);

    if (adjustment !== 0) {
      console.log(`⚖️ Event ${event.event_number}: ${event.duration_minutes} → ${newDuration} (${adjustment > 0 ? '+' : ''}${adjustment})`);
    }

    return {
      ...event,
      duration_minutes: newDuration
    };
  });
}

/**
 * Strategy 2: Pedagogical Priority Redistribution
 * Redistribute based on educational importance and flexibility of each event
 */
export function redistributeByPedagogicalPriority(events, targetTotalDuration, lessonFocus = 'balanced') {
  const currentTotal = events.reduce((sum, event) => sum + event.duration_minutes, 0);
  const timeDifference = targetTotalDuration - currentTotal;

  if (Math.abs(timeDifference) <= 1) return events;

  // Define flexibility and importance weights for each Gagne event
  const eventPriorities = {
    theoretical: {
      1: { flexibility: 0.3, importance: 0.7 }, // Gain Attention - somewhat flexible
      2: { flexibility: 0.8, importance: 0.4 }, // Inform Objectives - very flexible
      3: { flexibility: 0.5, importance: 0.8 }, // Stimulate Recall - important for theory
      4: { flexibility: 0.2, importance: 1.0 }, // Present Content - critical, less flexible
      5: { flexibility: 0.6, importance: 0.7 }, // Provide Guidance - moderately flexible
      6: { flexibility: 0.4, importance: 0.8 }, // Elicit Performance - important
      7: { flexibility: 0.7, importance: 0.6 }, // Provide Feedback - flexible
      8: { flexibility: 0.5, importance: 0.7 }, // Assess Performance - moderately flexible
      9: { flexibility: 0.8, importance: 0.5 }  // Enhance Retention - very flexible
    },
    practical: {
      1: { flexibility: 0.4, importance: 0.6 },
      2: { flexibility: 0.9, importance: 0.3 },
      3: { flexibility: 0.6, importance: 0.6 },
      4: { flexibility: 0.4, importance: 0.8 },
      5: { flexibility: 0.3, importance: 0.9 }, // Very important for practical lessons
      6: { flexibility: 0.2, importance: 1.0 }, // Critical for hands-on learning
      7: { flexibility: 0.3, importance: 0.9 }, // Essential feedback for skills
      8: { flexibility: 0.4, importance: 0.8 },
      9: { flexibility: 0.7, importance: 0.6 }
    },
    balanced: {
      1: { flexibility: 0.35, importance: 0.65 },
      2: { flexibility: 0.85, importance: 0.35 },
      3: { flexibility: 0.55, importance: 0.7 },
      4: { flexibility: 0.3, importance: 0.9 },
      5: { flexibility: 0.45, importance: 0.8 },
      6: { flexibility: 0.3, importance: 0.9 },
      7: { flexibility: 0.5, importance: 0.75 },
      8: { flexibility: 0.45, importance: 0.75 },
      9: { flexibility: 0.75, importance: 0.55 }
    }
  };

  const priorities = eventPriorities[lessonFocus] || eventPriorities.balanced;

  console.log(`🎯 Pedagogical redistribution (${lessonFocus} focus): ${timeDifference > 0 ? 'adding' : 'removing'} ${Math.abs(timeDifference)} minutes`);

  // Calculate redistribution weights based on flexibility
  const totalFlexibilityWeight = events.reduce((sum, event) =>
    sum + priorities[event.event_number].flexibility, 0);

  return events.map(event => {
    const eventPriority = priorities[event.event_number];
    const flexibilityWeight = eventPriority.flexibility / totalFlexibilityWeight;
    const adjustment = Math.round(timeDifference * flexibilityWeight);
    const newDuration = Math.max(1, event.duration_minutes + adjustment);

    if (adjustment !== 0) {
      console.log(`🎓 Event ${event.event_number} (${event.event_name}): ${event.duration_minutes} → ${newDuration} (${adjustment > 0 ? '+' : ''}${adjustment}) [flex: ${eventPriority.flexibility}]`);
    }

    return {
      ...event,
      duration_minutes: newDuration
    };
  });
}

/**
 * Strategy 3: Smart Adjacent Redistribution
 * Redistribute time from events adjacent to the modified ones
 */
export function redistributeAdjacent(events, modifiedEventNumbers, timeDifference) {
  if (Math.abs(timeDifference) <= 1) return events;

  console.log(`🔄 Adjacent redistribution: ${timeDifference > 0 ? 'need to remove' : 'need to add'} ${Math.abs(timeDifference)} minutes`);

  // Find events adjacent to modified ones
  const adjacentEvents = [];
  modifiedEventNumbers.forEach(eventNum => {
    if (eventNum > 1) adjacentEvents.push(eventNum - 1);
    if (eventNum < 9) adjacentEvents.push(eventNum + 1);
  });

  // Remove duplicates and events that were already modified
  const uniqueAdjacentEvents = [...new Set(adjacentEvents)]
    .filter(num => !modifiedEventNumbers.includes(num));

  if (uniqueAdjacentEvents.length === 0) {
    // Fallback to proportional if no adjacent events available
    return redistributeProportionally(events, events.reduce((sum, e) => sum + e.duration_minutes, 0) - timeDifference);
  }

  // Distribute the time difference among adjacent events
  const adjustmentPerEvent = Math.round(timeDifference / uniqueAdjacentEvents.length);
  let remainingAdjustment = timeDifference;

  return events.map(event => {
    if (uniqueAdjacentEvents.includes(event.event_number)) {
      const adjustment = Math.min(Math.abs(adjustmentPerEvent), Math.abs(remainingAdjustment)) *
                        (timeDifference > 0 ? -1 : 1); // Opposite of time difference
      remainingAdjustment -= adjustment;
      const newDuration = Math.max(1, event.duration_minutes + adjustment);

      console.log(`🔗 Adjacent Event ${event.event_number}: ${event.duration_minutes} → ${newDuration} (${adjustment > 0 ? '+' : ''}${adjustment})`);

      return {
        ...event,
        duration_minutes: newDuration
      };
    }
    return event;
  });
}

/**
 * Detect which events were modified by comparing before/after
 */
export function detectModifiedEvents(originalEvents, modifiedEvents) {
  const modified = [];

  for (let i = 0; i < originalEvents.length && i < modifiedEvents.length; i++) {
    if (originalEvents[i].duration_minutes !== modifiedEvents[i].duration_minutes) {
      modified.push(originalEvents[i].event_number);
    }
  }

  return modified;
}

/**
 * Determine lesson focus based on Bloom's levels
 */
export function determineLessonFocus(bloomLevels) {
  if (!bloomLevels || bloomLevels.length === 0) return 'balanced';

  const practicalLevels = ['apply', 'analyze', 'evaluate', 'create'];
  const theoreticalLevels = ['remember', 'understand'];

  const practicalCount = bloomLevels.filter(level => practicalLevels.includes(level)).length;
  const theoreticalCount = bloomLevels.filter(level => theoreticalLevels.includes(level)).length;

  if (practicalCount > theoreticalCount) return 'practical';
  if (theoreticalCount > practicalCount) return 'theoretical';
  return 'balanced';
}

/**
 * Strategy 4: Intelligent Auto-Balance
 * Combines multiple strategies based on the situation
 */
export function intelligentAutoBalance(
  events,
  targetTotalDuration,
  originalEvents = null,
  bloomLevels = []
) {
  const currentTotal = events.reduce((sum, event) => sum + event.duration_minutes, 0);
  const timeDifference = targetTotalDuration - currentTotal;

  console.log(`🤖 Intelligent auto-balance initiated:`);
  console.log(`📊 Current total: ${currentTotal} minutes`);
  console.log(`🎯 Target total: ${targetTotalDuration} minutes`);
  console.log(`⚖️ Time difference: ${timeDifference} minutes`);

  if (Math.abs(timeDifference) <= 1) {
    console.log(`✅ No redistribution needed (difference: ${timeDifference})`);
    return {
      events,
      strategy: 'none',
      adjustments: [],
      summary: `No redistribution needed (difference: ${timeDifference} minute${Math.abs(timeDifference) !== 1 ? 's' : ''})`
    };
  }

  // Detect which events were modified (if we have original events)
  const modifiedEventNumbers = originalEvents ? detectModifiedEvents(originalEvents, events) : [];
  console.log(`🔧 Modified events: ${modifiedEventNumbers.join(', ') || 'none detected'}`);

  // Determine lesson focus for pedagogical redistribution
  const lessonFocus = determineLessonFocus(bloomLevels);
  console.log(`🎯 Lesson focus: ${lessonFocus}`);

  // Strategy selection based on situation
  let redistributedEvents;
  let strategy;
  let rationale;

  if (Math.abs(timeDifference) <= 5 && modifiedEventNumbers.length > 0 && modifiedEventNumbers.length <= 2) {
    // Small changes with specific modifications: try adjacent redistribution first
    strategy = 'adjacent';
    rationale = `Small change (${timeDifference} minutes) with specific event modifications`;
    console.log(`🎯 Using adjacent redistribution: ${rationale}`);
    redistributedEvents = redistributeAdjacent(events, modifiedEventNumbers, timeDifference);
  } else if (Math.abs(timeDifference) > 10) {
    // Large changes: use pedagogical priority to maintain educational effectiveness
    strategy = 'pedagogical';
    rationale = `Large change (${timeDifference} minutes) requires pedagogical prioritization`;
    console.log(`🎓 Using pedagogical priority redistribution: ${rationale}`);
    redistributedEvents = redistributeByPedagogicalPriority(events, targetTotalDuration, lessonFocus);
  } else {
    // Medium changes or uncertain modifications: use proportional
    strategy = 'proportional';
    rationale = `Medium change (${timeDifference} minutes) using balanced proportional distribution`;
    console.log(`⚖️ Using proportional redistribution: ${rationale}`);
    redistributedEvents = redistributeProportionally(events, targetTotalDuration);
  }

  // Calculate adjustments made for reporting
  const adjustments = events.map((event, index) => {
    const newEvent = redistributedEvents[index];
    const adjustment = newEvent.duration_minutes - event.duration_minutes;
    return {
      eventNumber: event.event_number,
      eventName: event.event_name,
      originalDuration: event.duration_minutes,
      newDuration: newEvent.duration_minutes,
      adjustment,
      wasModified: modifiedEventNumbers.includes(event.event_number)
    };
  }).filter(adj => adj.adjustment !== 0);

  // Validate final result
  const finalTotal = redistributedEvents.reduce((sum, event) => sum + event.duration_minutes, 0);
  const finalDifference = Math.abs(finalTotal - targetTotalDuration);

  if (finalDifference > 2) {
    console.warn(`⚠️ Redistribution not optimal (difference: ${finalDifference}), applying final adjustment`);
    // Apply final micro-adjustments to most flexible events
    const flexibleEventNumbers = [2, 7, 9]; // Most flexible events (Inform Objectives, Provide Feedback, Enhance Retention)
    const remainingAdjustment = targetTotalDuration - finalTotal;

    redistributedEvents = redistributedEvents.map(event => {
      if (flexibleEventNumbers.includes(event.event_number) && remainingAdjustment !== 0) {
        const microAdjust = Math.sign(remainingAdjustment);
        const newDuration = Math.max(1, event.duration_minutes + microAdjust);

        if (newDuration !== event.duration_minutes) {
          console.log(`🔧 Micro-adjustment Event ${event.event_number}: ${event.duration_minutes} → ${newDuration}`);

          // Update adjustments array
          const existingAdjustment = adjustments.find(adj => adj.eventNumber === event.event_number);
          if (existingAdjustment) {
            existingAdjustment.newDuration = newDuration;
            existingAdjustment.adjustment = newDuration - existingAdjustment.originalDuration;
          } else {
            adjustments.push({
              eventNumber: event.event_number,
              eventName: event.event_name,
              originalDuration: event.duration_minutes,
              newDuration: newDuration,
              adjustment: microAdjust,
              wasModified: false
            });
          }

          return {
            ...event,
            duration_minutes: newDuration
          };
        }
      }
      return event;
    });

    strategy += '+micro';
    rationale += ' with micro-adjustments for precision';
  }

  const finalTotalAfterMicro = redistributedEvents.reduce((sum, event) => sum + event.duration_minutes, 0);
  const finalDifferenceAfterMicro = Math.abs(finalTotalAfterMicro - targetTotalDuration);

  console.log(`✅ Redistribution ${finalDifferenceAfterMicro <= 1 ? 'successful' : 'completed'} (final difference: ${finalDifferenceAfterMicro})`);

  // Generate summary
  const summary = generateRedistributionSummary(strategy, adjustments, timeDifference, finalDifferenceAfterMicro);

  return {
    events: redistributedEvents,
    strategy,
    rationale,
    adjustments,
    summary,
    timeDifference,
    finalDifference: finalDifferenceAfterMicro,
    modifiedEvents: modifiedEventNumbers
  };
}

/**
 * Generate human-readable summary of redistribution
 */
function generateRedistributionSummary(strategy, adjustments, originalDifference, finalDifference) {
  const strategyNames = {
    'adjacent': 'Adjacent Events',
    'pedagogical': 'Pedagogical Priority',
    'proportional': 'Proportional Distribution',
    'adjacent+micro': 'Adjacent Events with Fine-tuning',
    'pedagogical+micro': 'Pedagogical Priority with Fine-tuning',
    'proportional+micro': 'Proportional Distribution with Fine-tuning'
  };

  const strategyName = strategyNames[strategy] || strategy;
  const adjustmentCount = adjustments.length;
  const totalAdjustment = adjustments.reduce((sum, adj) => sum + Math.abs(adj.adjustment), 0);

  let summary = `Applied ${strategyName} strategy: `;

  if (adjustmentCount === 0) {
    summary += 'No adjustments needed';
  } else {
    summary += `${adjustmentCount} event${adjustmentCount !== 1 ? 's' : ''} adjusted`;
    if (finalDifference <= 1) {
      summary += `, perfect balance achieved`;
    } else {
      summary += `, ${finalDifference} minute${finalDifference !== 1 ? 's' : ''} difference remaining`;
    }
  }

  return summary;
}

/**
 * Format adjustments for user display
 */
export function formatAdjustments(adjustments) {
  if (!adjustments || adjustments.length === 0) {
    return 'No time adjustments made';
  }

  return adjustments.map(adj => {
    const sign = adj.adjustment > 0 ? '+' : '';
    const modifiedText = adj.wasModified ? ' (user modified)' : '';
    return `Event ${adj.eventNumber}: ${formatDuration(adj.originalDuration)} → ${formatDuration(adj.newDuration)} (${sign}${adj.adjustment}min)${modifiedText}`;
  }).join('\n');
}

export default {
  redistributeProportionally,
  redistributeByPedagogicalPriority,
  redistributeAdjacent,
  intelligentAutoBalance,
  detectModifiedEvents,
  determineLessonFocus,
  formatAdjustments
};