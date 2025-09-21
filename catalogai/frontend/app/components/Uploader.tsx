'use client';

import { useState, useCallback, useRef } from 'react';
import { cn } from '../lib/utils';
import { formatFileSize } from '../api';
import { Upload, X, Image, FileImage } from 'lucide-react';

interface UploaderProps {
  onFilesSelected: (files: File[]) => void;
  isUploading?: boolean;
  maxFiles?: number;
  maxFileSize?: number;
  acceptedTypes?: string[];
  className?: string;
}

export function Uploader({
  onFilesSelected,
  isUploading = false,
  maxFiles = 10,
  maxFileSize = 8,
  acceptedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
  className,
}: UploaderProps) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFiles = (files: File[]): { valid: File[]; errors: string[] } => {
    const valid: File[] = [];
    const errors: string[] = [];

    if (files.length > maxFiles) {
      errors.push(`Maximum ${maxFiles} files allowed`);
      return { valid, errors };
    }

    for (const file of files) {
      if (!acceptedTypes.includes(file.type)) {
        errors.push(`${file.name}: Invalid file type. Accepted: ${acceptedTypes.join(', ')}`);
        continue;
      }

      if (file.size > maxFileSize * 1024 * 1024) {
        errors.push(`${file.name}: File too large. Maximum ${maxFileSize}MB`);
        continue;
      }

      valid.push(file);
    }

    return { valid, errors };
  };

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return;

    const fileArray = Array.from(files);
    const { valid, errors } = validateFiles(fileArray);

    if (errors.length > 0) alert(errors.join('\n'));

    if (valid.length > 0) {
      setSelectedFiles(valid);
      onFilesSelected(valid);
    }
  }, [onFilesSelected, maxFiles, maxFileSize, acceptedTypes]);

  const handleDragOver = useCallback((e: any) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: any) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e: any) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const handleFileInput = useCallback((e: any) => {
    handleFiles(e.target.files);
  }, [handleFiles]);

  const handleClick = () => {
    if (!isUploading) {
      fileInputRef.current?.click();
    }
  };

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
    onFilesSelected(newFiles);
  };

  const clearFiles = () => {
    setSelectedFiles([]);
    onFilesSelected([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className={cn('w-full space-y-6', className)}>
      <div
        className={cn(
          'upload-area relative overflow-hidden',
          dragOver && 'drag-over',
          isUploading && 'pointer-events-none opacity-50'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileInput}
          className="hidden"
          disabled={isUploading}
        />
        
        <div className="absolute inset-0 opacity-5">
          <div className="grid grid-cols-8 gap-4 h-full">
            {Array.from({ length: 32 }).map((_, i) => (
              <div key={i} className="bg-primary-500 rounded-full"></div>
            ))}
          </div>
        </div>
        
        <div className="relative text-center space-y-6">
          <div className="flex justify-center">
            <div className={cn(
              "relative p-6 rounded-3xl transition-all duration-300",
              dragOver 
                ? "bg-primary-100 scale-110" 
                : "bg-gradient-to-br from-primary-50 to-secondary-50 group-hover:scale-105"
            )}>
              <Upload className={cn(
                "w-12 h-12 transition-colors duration-300",
                dragOver ? "text-primary-600" : "text-primary-500"
              )} />
              {dragOver && (<div className="absolute inset-0 bg-primary-500/20 rounded-3xl animate-pulse"></div>)}
            </div>
          </div>

          <div className="space-y-3">
            <div className="text-2xl font-bold text-neutral-900">
              {isUploading ? (
                <span className="flex items-center justify-center space-x-2">
                  <div className="loading-spinner-lg"></div>
                  <span>Processing Images...</span>
                </span>
              ) : dragOver ? (
                'Drop your images here'
              ) : (
                'Drop images here or click to browse'
              )}
            </div>
            <div className="text-neutral-600 space-y-1">
              <p>Supports JPEG, PNG, WebP, GIF up to {maxFileSize}MB each</p>
              <p className="text-sm">Maximum {maxFiles} files per upload</p>
            </div>
          </div>

          {!isUploading && !dragOver && (
            <div className="pt-2">
              <button className="btn-primary btn-lg">
                <Upload className="w-5 h-5 mr-2" />
                Choose Files
              </button>
            </div>
          )}
        </div>
      </div>

      {selectedFiles.length > 0 && (
        <div className="space-y-4 animate-slide-up">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-neutral-900 flex items-center space-x-2">
              <FileImage className="w-5 h-5 text-primary-600" />
              <span>Selected Files ({selectedFiles.length})</span>
            </h3>
            <button
              onClick={clearFiles}
              className="btn-ghost btn-sm text-danger-600 hover:text-danger-700"
              disabled={isUploading}
            >
              <X className="w-4 h-4 mr-1" />
              Clear All
            </button>
          </div>
          
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {selectedFiles.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="card p-4 hover-lift"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 min-w-0 flex-1">
                    <div className="p-2 bg-gradient-to-br from-primary-100 to-secondary-100 rounded-xl">
                      <Image className="w-6 h-6 text-primary-600" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="font-medium text-neutral-900 truncate">
                        {file.name}
                      </div>
                      <div className="flex items-center space-x-3 text-sm text-neutral-500 mt-1">
                        <span>{formatFileSize(file.size)}</span>
                        <span>•</span>
                        <span className="uppercase">{file.type.split('/')[1]}</span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="btn-ghost p-2 text-neutral-400 hover:text-danger-600 hover:bg-danger-50"
                    disabled={isUploading}
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}