/**
 * Documents Page - Main document management interface
 * Story 3: Document Management - Page integration
 */

import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Paper,
  Grid,
} from '@mui/material';
import DocumentList from '@/features/documents/components/DocumentList';
import DocumentUpload from '@/features/documents/components/DocumentUpload';
import DocumentPreview from '@/features/documents/components/DocumentPreview';
import FolderTree from '@/features/documents/components/FolderTree';
import { Document } from '@/features/documents/api/documentsApi';

const DocumentsPage: React.FC = () => {
  const { dealId } = useParams<{ dealId?: string }>();
  const [selectedFolder, setSelectedFolder] = useState<string>('/');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [previewDocument, setPreviewDocument] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleFolderSelect = (path: string) => {
    setSelectedFolder(path);
  };

  const handleUploadClick = () => {
    setUploadDialogOpen(true);
  };

  const handleUploadComplete = () => {
    setRefreshKey((prev) => prev + 1);
    setUploadDialogOpen(false);
  };

  const handleDocumentClick = (document: Document) => {
    setPreviewDocument(document.id);
  };

  const handleNewFolder = (path: string) => {
    // Folder creation is handled by FolderTree component
    console.log('New folder at:', path);
  };

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <Box sx={{ height: 'calc(100vh - 64px)', display: 'flex', p: 2, gap: 2 }}>
      {/* Folder Navigation */}
      <Paper sx={{ width: 280, overflow: 'auto' }}>
        <FolderTree
          dealId={dealId}
          selectedPath={selectedFolder}
          onFolderSelect={handleFolderSelect}
          onRefresh={handleRefresh}
        />
      </Paper>

      {/* Document List */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <DocumentList
          key={refreshKey}
          dealId={dealId}
          folderPath={selectedFolder}
          onUploadClick={handleUploadClick}
          onDocumentClick={handleDocumentClick}
          onFolderClick={handleNewFolder}
        />
      </Box>

      {/* Upload Dialog */}
      <DocumentUpload
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        dealId={dealId}
        folderPath={selectedFolder}
        onUploadComplete={handleUploadComplete}
      />

      {/* Document Preview */}
      <DocumentPreview
        documentId={previewDocument}
        open={!!previewDocument}
        onClose={() => setPreviewDocument(null)}
      />
    </Box>
  );
};

export default DocumentsPage;