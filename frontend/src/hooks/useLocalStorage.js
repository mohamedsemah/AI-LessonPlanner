import { useState, useEffect } from 'react';

/**
 * Custom hook for localStorage with JSON serialization
 */
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  };

  const removeValue = () => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue, removeValue];
}

/**
 * Hook for lesson draft management
 */
export function useLessonDraft() {
  const [draft, setDraft, removeDraft] = useLocalStorage('lessonDraft', null);
  const [autosaveEnabled, setAutosaveEnabled] = useState(true);

  useEffect(() => {
    if (!autosaveEnabled) return;

    const interval = setInterval(() => {
      if (draft) {
        console.log('Auto-saved lesson draft');
      }
    }, 30000); // Auto-save every 30 seconds

    return () => clearInterval(interval);
  }, [draft, autosaveEnabled]);

  const saveDraft = (lessonData) => {
    const draftData = {
      ...lessonData,
      lastSaved: new Date().toISOString()
    };
    setDraft(draftData);
  };

  const clearDraft = () => {
    removeDraft();
  };

  const hasDraft = Boolean(draft);

  return {
    draft,
    saveDraft,
    clearDraft,
    hasDraft,
    autosaveEnabled,
    setAutosaveEnabled
  };
}

/**
 * Hook for form persistence
 */
export function useFormPersistence(formKey, defaultValues = {}) {
  const [persistedData, setPersistedData, removePersistedData] = useLocalStorage(
    `form_${formKey}`,
    defaultValues
  );

  const saveFormData = (formData) => {
    setPersistedData({
      ...formData,
      lastUpdated: new Date().toISOString()
    });
  };

  const clearFormData = () => {
    removePersistedData();
  };

  const hasPersistedData = Boolean(
    persistedData && Object.keys(persistedData).length > 0
  );

  return {
    persistedData,
    saveFormData,
    clearFormData,
    hasPersistedData
  };
}