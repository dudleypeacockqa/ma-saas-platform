/**
 * Document Upload Component with Drag & Drop
 * Story 3.3: Drag-Drop Upload - Main upload component
 */

import React, { useState, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Button,
  Typography,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Stack,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormControlLabel,
  Switch,
  Autocomplete,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  InsertDriveFile as FileIcon,
  Close as CloseIcon,
  Delete as DeleteIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useDropzone, Accept } from 'react-dropzone';
import {
  useUploadDocumentMutation,
  useGetPresignedUploadUrlMutation,
  formatFileSize,
  getFileIcon,
} from '../api/documentsApi';

interface DocumentUploadProps {
  open: boolean;
  onClose: () => void;
  dealId?: string;
  folderPath?: string;
  onUploadComplete?: () => void;
}

interface FileUploadItem {
  file: File;
  id: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
  documentType?: string;
  title?: string;
  description?: string;
  tags?: string[];
  isConfidential?: boolean;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  open,
  onClose,
  dealId,
  folderPath = '/',
  onUploadComplete,
}) => {
  const [files, setFiles] = useState<FileUploadItem[]>([]);
  const [uploadDocument] = useUploadDocumentMutation();
  const [getPresignedUrl] = useGetPresignedUploadUrlMutation();

  // Dropzone configuration
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: FileUploadItem[] = acceptedFiles.map((file) => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending' as const,
      progress: 0,
      documentType: 'other',
      isConfidential: true,
      tags: [],
    }));
    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
    maxSize: 524288000, // 500MB
  });

  // File management
  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  const updateFile = useCallback((id: string, updates: Partial<FileUploadItem>) => {
    setFiles((prev) =>
      prev.map((f) => (f.id === id ? { ...f, ...updates } : f))
    );
  }, []);

  // Upload handlers
  const uploadFile = async (fileItem: FileUploadItem) => {
    try {
      updateFile(fileItem.id, { status: 'uploading', progress: 10 });

      // Create FormData
      const formData = new FormData();
      formData.append('file', fileItem.file);
      if (fileItem.title) formData.append('title', fileItem.title);
      if (fileItem.description) formData.append('description', fileItem.description);
      if (fileItem.documentType) formData.append('document_type', fileItem.documentType);
      if (dealId) formData.append('deal_id', dealId);
      formData.append('folder_path', folderPath);
      if (fileItem.tags && fileItem.tags.length > 0) {
        formData.append('tags', JSON.stringify(fileItem.tags));
      }
      formData.append('is_confidential', String(fileItem.isConfidential));

      // Simulate progress
      const progressInterval = setInterval(() => {
        updateFile(fileItem.id, {
          progress: (prev) => Math.min(prev + 10, 90),
        });
      }, 200);

      // Upload
      const result = await uploadDocument(formData).unwrap();

      clearInterval(progressInterval);
      updateFile(fileItem.id, {
        status: 'success',
        progress: 100,
      });

      return result;
    } catch (error: any) {
      updateFile(fileItem.id, {
        status: 'error',
        error: error.message || 'Upload failed',
      });
      throw error;
    }
  };

  const handleUploadAll = async () => {
    const pendingFiles = files.filter((f) => f.status === 'pending');

    // Upload files in parallel (max 3 at a time)
    const uploadPromises = [];
    for (let i = 0; i < pendingFiles.length; i += 3) {
      const batch = pendingFiles.slice(i, i + 3);
      const batchPromises = batch.map((file) => uploadFile(file));
      await Promise.allSettled(batchPromises);
    }

    // Check if all uploads completed
    const allSuccess = files.every((f) => f.status === 'success');
    if (allSuccess && onUploadComplete) {
      onUploadComplete();
      handleClose();
    }
  };

  const handleClose = () => {
    if (files.some((f) => f.status === 'uploading')) {
      if (!window.confirm('Files are still uploading. Cancel anyway?')) {
        return;
      }
    }
    setFiles([]);
    onClose();
  };

  const pendingCount = files.filter((f) => f.status === 'pending').length;
  const uploadingCount = files.filter((f) => f.status === 'uploading').length;
  const successCount = files.filter((f) => f.status === 'success').length;
  const errorCount = files.filter((f) => f.status === 'error').length;

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '60vh' },
      }}
    >
      <DialogTitle>
        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">Upload Documents</Typography>
          <IconButton onClick={handleClose} size="small">
            <CloseIcon />
          </IconButton>
        </Stack>
      </DialogTitle>

      <DialogContent>
        {/* Dropzone */}
        {files.length === 0 ? (
          <Box
            {...getRootProps()}
            sx={{
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'divider',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              bgcolor: isDragActive ? 'action.hover' : 'background.paper',
              transition: 'all 0.2s',
              minHeight: 300,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <input {...getInputProps()} />
            <UploadIcon sx={{ fontSize: 64, color: 'action.disabled', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive
                ? 'Drop files here'
                : 'Drag & drop files here, or click to select'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Maximum file size: 500MB
            </Typography>
            <Button
              variant="contained"
              startIcon={<UploadIcon />}
              sx={{ mt: 2 }}
              onClick={(e) => e.stopPropagation()}
            >
              Select Files
            </Button>
          </Box>
        ) : (
          <>
            {/* File list */}
            <List sx={{ maxHeight: 400, overflow: 'auto' }}>
              {files.map((fileItem) => (
                <ListItem key={fileItem.id} sx={{ flexDirection: 'column', alignItems: 'stretch' }}>
                  <Box sx={{ display: 'flex', width: '100%', mb: 1 }}>
                    <ListItemIcon>
                      {fileItem.status === 'success' ? (
                        <SuccessIcon color="success" />
                      ) : fileItem.status === 'error' ? (
                        <ErrorIcon color="error" />
                      ) : (
                        <FileIcon />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={fileItem.title || fileItem.file.name}
                      secondary={
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Typography variant="caption">
                            {formatFileSize(fileItem.file.size)}
                          </Typography>
                          {fileItem.status === 'uploading' && (
                            <Typography variant="caption">
                              Uploading... {fileItem.progress}%
                            </Typography>
                          )}
                          {fileItem.status === 'error' && (
                            <Typography variant="caption" color="error">
                              {fileItem.error}
                            </Typography>
                          )}
                        </Stack>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        onClick={() => removeFile(fileItem.id)}
                        disabled={fileItem.status === 'uploading'}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </Box>

                  {/* Progress bar */}
                  {fileItem.status === 'uploading' && (
                    <LinearProgress
                      variant="determinate"
                      value={fileItem.progress}
                      sx={{ mb: 1 }}
                    />
                  )}

                  {/* File metadata (only for pending files) */}
                  {fileItem.status === 'pending' && (
                    <Box sx={{ pl: 7, pr: 5, pb: 2 }}>
                      <Stack spacing={1}>
                        <Stack direction="row" spacing={1}>
                          <TextField
                            size="small"
                            label="Title"
                            value={fileItem.title || ''}
                            onChange={(e) =>
                              updateFile(fileItem.id, { title: e.target.value })
                            }
                            fullWidth
                          />
                          <FormControl size="small" sx={{ minWidth: 150 }}>
                            <InputLabel>Type</InputLabel>
                            <Select
                              value={fileItem.documentType || 'other'}
                              onChange={(e) =>
                                updateFile(fileItem.id, {
                                  documentType: e.target.value,
                                })
                              }
                              label="Type"
                            >
                              <MenuItem value="nda">NDA</MenuItem>
                              <MenuItem value="loi">LOI</MenuItem>
                              <MenuItem value="term_sheet">Term Sheet</MenuItem>
                              <MenuItem value="due_diligence">Due Diligence</MenuItem>
                              <MenuItem value="financial_statement">Financial</MenuItem>
                              <MenuItem value="legal_document">Legal</MenuItem>
                              <MenuItem value="presentation">Presentation</MenuItem>
                              <MenuItem value="report">Report</MenuItem>
                              <MenuItem value="contract">Contract</MenuItem>
                              <MenuItem value="other">Other</MenuItem>
                            </Select>
                          </FormControl>
                        </Stack>

                        <TextField
                          size="small"
                          label="Description"
                          value={fileItem.description || ''}
                          onChange={(e) =>
                            updateFile(fileItem.id, { description: e.target.value })
                          }
                          multiline
                          rows={2}
                          fullWidth
                        />

                        <Stack direction="row" spacing={1} alignItems="center">
                          <Autocomplete
                            multiple
                            size="small"
                            options={[]}
                            freeSolo
                            value={fileItem.tags || []}
                            onChange={(e, value) =>
                              updateFile(fileItem.id, { tags: value })
                            }
                            renderInput={(params) => (
                              <TextField {...params} label="Tags" placeholder="Add tags" />
                            )}
                            renderTags={(value, getTagProps) =>
                              value.map((option, index) => (
                                <Chip
                                  size="small"
                                  label={option}
                                  {...getTagProps({ index })}
                                />
                              ))
                            }
                            sx={{ flexGrow: 1 }}
                          />
                          <FormControlLabel
                            control={
                              <Switch
                                checked={fileItem.isConfidential !== false}
                                onChange={(e) =>
                                  updateFile(fileItem.id, {
                                    isConfidential: e.target.checked,
                                  })
                                }
                              />
                            }
                            label="Confidential"
                          />
                        </Stack>
                      </Stack>
                    </Box>
                  )}
                </ListItem>
              ))}
            </List>

            {/* Add more files button */}
            <Box {...getRootProps()} sx={{ mt: 2 }}>
              <input {...getInputProps()} />
              <Button
                variant="outlined"
                startIcon={<UploadIcon />}
                fullWidth
              >
                Add More Files
              </Button>
            </Box>
          </>
        )}

        {/* Status summary */}
        {files.length > 0 && (
          <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
            {pendingCount > 0 && (
              <Chip label={`${pendingCount} pending`} size="small" />
            )}
            {uploadingCount > 0 && (
              <Chip label={`${uploadingCount} uploading`} size="small" color="primary" />
            )}
            {successCount > 0 && (
              <Chip label={`${successCount} completed`} size="small" color="success" />
            )}
            {errorCount > 0 && (
              <Chip label={`${errorCount} failed`} size="small" color="error" />
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={handleUploadAll}
          disabled={pendingCount === 0 || uploadingCount > 0}
          startIcon={<UploadIcon />}
        >
          Upload {pendingCount > 0 && `(${pendingCount})`}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentUpload;