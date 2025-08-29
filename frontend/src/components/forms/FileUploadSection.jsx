import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, FileText, FileImage, File, AlertCircle, CheckCircle } from 'lucide-react';

const FileUploadSection = ({ uploadedFiles, onFilesChange, error }) => {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const MAX_FILES = 5;
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  const ALLOWED_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp'
  ];

  const getFileIcon = (file) => {
    if (file.type.startsWith('image/')) return <FileImage className="w-4 h-4" />;
    if (file.type === 'application/pdf') return <FileText className="w-4 h-4" />;
    if (file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') return <File className="w-4 h-4" />;
    return <FileText className="w-4 h-4" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const validateFile = (file) => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return { valid: false, error: 'File type not supported. Please upload PDF, DOCX, TXT, or image files.' };
    }
    if (file.size > MAX_FILE_SIZE) {
      return { valid: false, error: `File size exceeds 10MB limit. Current size: ${formatFileSize(file.size)}` };
    }
    return { valid: true };
  };

  const handleFiles = (files) => {
    const fileArray = Array.from(files);
    const validFiles = [];
    const errors = [];

    fileArray.forEach(file => {
      const validation = validateFile(file);
      if (validation.valid) {
        validFiles.push(file);
      } else {
        errors.push(`${file.name}: ${validation.error}`);
      }
    });

    if (errors.length > 0) {
      errors.forEach(error => console.error(error));
    }

    if (validFiles.length > 0) {
      const newFiles = [...uploadedFiles, ...validFiles].slice(0, MAX_FILES);
      onFilesChange(newFiles);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const removeFile = (index) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index);
    onFilesChange(newFiles);
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          Upload Syllabus and Relevant Materials
        </label>
        <span className="text-xs text-gray-500">
          {uploadedFiles.length}/{MAX_FILES} files
        </span>
      </div>

      {/* File Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.jpg,.jpeg,.png,.gif,.webp"
          onChange={handleFileInput}
          className="hidden"
        />

        <div className="space-y-3">
          <Upload className={`mx-auto h-8 w-8 ${dragActive ? 'text-primary-500' : 'text-gray-400'}`} />
          <div>
            <p className="text-sm text-gray-600">
              <span className="font-medium">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500 mt-1">
              PDF, DOCX, TXT, or image files up to 10MB each
            </p>
          </div>
          <button
            type="button"
            onClick={openFileDialog}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
          >
            Choose Files
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="flex items-center gap-2 text-sm text-red-600">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* File List */}
      <AnimatePresence>
        {uploadedFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2"
          >
            <h4 className="text-sm font-medium text-gray-700">Uploaded Files:</h4>
            {uploadedFiles.map((file, index) => (
              <motion.div
                key={`${file.name}-${index}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border"
              >
                <div className="flex items-center gap-3">
                  {getFileIcon(file)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Helper Text */}
      <p className="text-xs text-gray-500">
        Upload course syllabus, relevant materials, images, graphs, or datasheets. The AI will analyze these files to create contextually appropriate lesson plans and content.
      </p>
    </div>
  );
};

export default FileUploadSection;
