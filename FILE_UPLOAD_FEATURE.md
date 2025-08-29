# File Upload Feature for Lesson Planning Tool

## Overview
The lesson planning tool now supports uploading syllabus and relevant materials (PDF, DOCX, TXT, and image files) to provide AI with contextual information for generating more accurate and contextually appropriate lesson plans.

## Features

### File Upload Capabilities
- **Supported Formats**: PDF, DOCX, TXT, JPEG, PNG, GIF, WebP
- **File Size Limit**: 10MB per file
- **Maximum Files**: Up to 5 files per lesson
- **Drag & Drop**: Modern drag-and-drop interface
- **File Validation**: Automatic file type and size validation

### AI Integration
- **Content Extraction**: AI reads and analyzes all uploaded content
- **Contextual Understanding**: AI uses uploaded materials to understand course progression
- **Prerequisite Awareness**: AI avoids referencing concepts not yet taught
- **Material Incorporation**: AI incorporates specific materials, images, and data into lesson plans

## How It Works

### 1. File Processing
- Files are converted to base64 and sent to the backend
- Backend processes each file type using appropriate libraries:
  - **PDF**: PyMuPDF for text extraction
  - **DOCX**: python-docx for document parsing
  - **TXT**: Direct text reading
  - **Images**: PIL + Tesseract OCR for text extraction and image description

### 2. Content Analysis
- Extracted content is categorized (syllabus, materials, images, data)
- AI context is generated summarizing all uploaded materials
- Content length and file metadata are tracked

### 3. AI Generation
- AI receives comprehensive context from uploaded materials
- Lesson objectives are generated considering course progression
- Lesson plans incorporate relevant materials and prerequisites
- Gagne events are designed with contextual activities

## Example Use Cases

### Data Structures Course
**Uploaded**: Course syllabus showing Chapter 1 covers Queues
**Result**: AI generates lesson plan focused only on Queues, avoiding references to Stacks or other advanced concepts

### Science Lab
**Uploaded**: Lab datasheets, equipment images, safety protocols
**Result**: AI incorporates specific equipment, safety requirements, and data analysis into lesson activities

### Literature Class
**Uploaded**: Course syllabus, reading materials, historical context documents
**Result**: AI creates lesson plan with appropriate prerequisites and contextual references

## Technical Implementation

### Frontend Changes
- New `FileUploadSection` component with drag-and-drop
- File validation and error handling
- Base64 conversion before API submission
- Progress indicators for file processing

### Backend Changes
- New `FileProcessingService` for content extraction
- Updated `LessonRequest` model to handle file data
- Enhanced AI prompts with uploaded content context
- File type-specific processing pipelines

### Dependencies Added
```
PyMuPDF==1.23.8      # PDF processing
python-docx==1.1.0   # DOCX processing
pytesseract==0.3.10  # OCR for images
```

## Benefits

1. **Contextual Accuracy**: AI understands course progression and prerequisites
2. **Material Integration**: Specific materials are incorporated into lesson plans
3. **Prerequisite Awareness**: No references to concepts not yet taught
4. **Rich Content**: Images, graphs, and datasheets enhance lesson quality
5. **Course Continuity**: Lessons build properly on previous knowledge

## User Experience

### Upload Process
1. Drag and drop files or click "Choose Files"
2. Files are validated for type and size
3. Uploaded files are displayed with metadata
4. Files can be removed individually

### Generation Process
1. Files are processed and converted to base64
2. Content is extracted and analyzed
3. AI generates lesson plan with full context
4. Results incorporate uploaded materials appropriately

## Error Handling

- **File Type Validation**: Only supported formats accepted
- **Size Validation**: Files over 10MB rejected
- **Processing Errors**: Failed files logged with error details
- **Fallback Behavior**: System continues with successfully processed files

## Future Enhancements

- **File Preview**: View uploaded files before generation
- **Content Highlighting**: Show which parts of uploaded content influenced AI
- **Batch Processing**: Process multiple lessons with same materials
- **Material Library**: Save and reuse common materials across lessons
- **Advanced OCR**: Better image analysis and diagram recognition
