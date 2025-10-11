/**
 * Document Preview Component
 * Story 3.2: Document List UI - Preview functionality
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Button,
  IconButton,
  Typography,
  Chip,
  Stack,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  TextField,
} from '@mui/material';
import {
  Close as CloseIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Edit as EditIcon,
  History as HistoryIcon,
  Info as InfoIcon,
  Person as PersonIcon,
  CalendarToday as CalendarIcon,
  Storage as StorageIcon,
  Lock as LockIcon,
  LockOpen as LockOpenIcon,
  Label as LabelIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import {
  useGetDocumentQuery,
  useGetDocumentVersionsQuery,
  useUpdateDocumentMutation,
  useGetDownloadUrlQuery,
  formatFileSize,
  getDocumentTypeColor,
  Document,
} from '../api/documentsApi';

interface DocumentPreviewProps {
  documentId: string | null;
  open: boolean;
  onClose: () => void;
  onEdit?: (document: Document) => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
  </div>
);

const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  documentId,
  open,
  onClose,
  onEdit,
}) => {
  const [tabValue, setTabValue] = useState(0);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // RTK Query hooks
  const { data: document, isLoading } = useGetDocumentQuery(documentId || '', {
    skip: !documentId,
  });
  const { data: versions } = useGetDocumentVersionsQuery(documentId || '', {
    skip: !documentId || tabValue !== 2,
  });
  const { data: downloadUrl } = useGetDownloadUrlQuery(documentId || '', {
    skip: !documentId,
  });
  const [updateDocument] = useUpdateDocumentMutation();

  // Load preview content
  useEffect(() => {
    if (document?.presigned_url) {
      setPreviewUrl(document.presigned_url);
    }
  }, [document]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleDownload = () => {
    if (downloadUrl?.url) {
      window.open(downloadUrl.url, '_blank');
    }
  };

  const handleShare = () => {
    if (document?.presigned_url) {
      navigator.clipboard.writeText(document.presigned_url);
      // Show success toast
    }
  };

  const isPreviewable = (mimeType: string) => {
    return (
      mimeType.startsWith('image/') ||
      mimeType === 'application/pdf' ||
      mimeType.startsWith('text/')
    );
  };

  if (!open || !documentId) {
    return null;
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      sx={{
        '& .MuiDialog-paper': {
          height: '90vh',
        },
      }}
    >
      <DialogTitle>
        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="h6">
              {document?.title || document?.original_filename || 'Loading...'}
            </Typography>
            {document && (
              <Stack direction="row" spacing={1} alignItems="center" mt={1}>
                <Chip
                  label={document.document_type.replace('_', ' ')}
                  size="small"
                  sx={{
                    bgcolor: getDocumentTypeColor(document.document_type) + '20',
                    color: getDocumentTypeColor(document.document_type),
                  }}
                />
                <Chip
                  icon={document.is_confidential ? <LockIcon /> : <LockOpenIcon />}
                  label={document.is_confidential ? 'Confidential' : 'Public'}
                  size="small"
                  variant="outlined"
                  color={document.is_confidential ? 'warning' : 'default'}
                />
                <Typography variant="caption" color="text.secondary">
                  v{document.version}
                </Typography>
              </Stack>
            )}
          </Box>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Stack>
      </DialogTitle>

      <DialogContent dividers>
        {isLoading ? (
          <Box display="flex" justifyContent="center" alignItems="center" height="100%">
            <CircularProgress />
          </Box>
        ) : document ? (
          <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Preview" />
              <Tab label="Details" />
              <Tab label="Versions" />
            </Tabs>

            <TabPanel value={tabValue} index={0}>
              <Box sx={{ height: 'calc(100% - 48px)', overflow: 'auto' }}>
                {isPreviewable(document.mime_type) ? (
                  <>
                    {document.mime_type.startsWith('image/') && (
                      <img
                        src={previewUrl || ''}
                        alt={document.original_filename}
                        style={{ maxWidth: '100%', height: 'auto' }}
                      />
                    )}
                    {document.mime_type === 'application/pdf' && (
                      <iframe
                        src={previewUrl || ''}
                        title={document.original_filename}
                        width="100%"
                        height="100%"
                        style={{ border: 'none' }}
                      />
                    )}
                    {document.mime_type.startsWith('text/') && (
                      <iframe
                        src={previewUrl || ''}
                        title={document.original_filename}
                        width="100%"
                        height="100%"
                        style={{ border: 'none' }}
                      />
                    )}
                  </>
                ) : (
                  <Alert severity="info">
                    Preview not available for this file type. Click download to view.
                  </Alert>
                )}
              </Box>
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <InfoIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="File Name"
                    secondary={document.original_filename}
                  />
                </ListItem>

                <ListItem>
                  <ListItemIcon>
                    <StorageIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="File Size"
                    secondary={formatFileSize(document.file_size)}
                  />
                </ListItem>

                <ListItem>
                  <ListItemIcon>
                    <CalendarIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Uploaded"
                    secondary={format(new Date(document.uploaded_at), 'PPpp')}
                  />
                </ListItem>

                <ListItem>
                  <ListItemIcon>
                    <CalendarIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Modified"
                    secondary={format(new Date(document.modified_at), 'PPpp')}
                  />
                </ListItem>

                <Divider sx={{ my: 2 }} />

                <ListItem>
                  <ListItemIcon>
                    <LabelIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Tags"
                    secondary={
                      <Stack direction="row" spacing={1} mt={1}>
                        {document.tags.map((tag, index) => (
                          <Chip key={index} label={tag} size="small" />
                        ))}
                      </Stack>
                    }
                  />
                </ListItem>

                {document.description && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <ListItem>
                      <ListItemText
                        primary="Description"
                        secondary={document.description}
                      />
                    </ListItem>
                  </>
                )}

                <Divider sx={{ my: 2 }} />

                <ListItem>
                  <ListItemText
                    primary="Statistics"
                    secondary={`${document.view_count} views • ${document.download_count} downloads`}
                  />
                </ListItem>
              </List>
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
              <List>
                {versions?.map((version) => (
                  <ListItem
                    key={version.id}
                    button
                    selected={version.id === document.id}
                  >
                    <ListItemText
                      primary={`Version ${version.version}`}
                      secondary={format(new Date(version.uploaded_at), 'PPp')}
                    />
                    {version.is_latest_version && (
                      <Chip label="Current" size="small" color="primary" />
                    )}
                  </ListItem>
                ))}
              </List>
            </TabPanel>
          </Box>
        ) : (
          <Alert severity="error">Document not found</Alert>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button
          startIcon={<ShareIcon />}
          onClick={handleShare}
          disabled={!document}
        >
          Share
        </Button>
        <Button
          startIcon={<EditIcon />}
          onClick={() => document && onEdit?.(document)}
          disabled={!document}
        >
          Edit
        </Button>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={handleDownload}
          disabled={!document}
        >
          Download
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentPreview;