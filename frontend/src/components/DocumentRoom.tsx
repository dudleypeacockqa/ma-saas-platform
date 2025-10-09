/**
 * Virtual Data Room (VDR) Component
 * Secure document management for due diligence
 * Features: folder structure, version control, access logging, document requests
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Breadcrumbs,
  Link,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Alert,
  LinearProgress,
  Menu,
  Divider,
  Avatar,
  AvatarGroup,
} from '@mui/material';
import {
  Folder as FolderIcon,
  InsertDriveFile as FileIcon,
  CloudUpload as UploadIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  MoreVert as MoreIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  History as HistoryIcon,
  Lock as LockIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CreateNewFolder as NewFolderIcon,
  NavigateNext as NavigateIcon,
} from '@mui/icons-material';

interface DocumentRoomProps {
  processId: string;
  readOnly?: boolean;
}

interface Folder {
  id: string;
  name: string;
  parent_id: string | null;
  document_count: number;
  created_at: string;
  updated_at: string;
}

interface Document {
  id: string;
  filename: string;
  title: string;
  folder_id: string;
  category: string;
  status: string;
  size: number;
  version: number;
  uploaded_by: string;
  uploaded_by_name: string;
  uploaded_at: string;
  reviewed_by: string | null;
  reviewed_by_name: string | null;
  reviewed_at: string | null;
  review_status: string;
  access_level: string;
  is_confidential: boolean;
  download_count: number;
  view_count: number;
}

interface DocumentRequest {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: string;
  status: string;
  due_date: string;
  requested_by: string;
  fulfilled_by_document_id: string | null;
}

const DocumentRoom: React.FC<DocumentRoomProps> = ({ processId, readOnly = false }) => {
  const { getToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Data states
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(null);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [documentRequests, setDocumentRequests] = useState<DocumentRequest[]>([]);
  const [breadcrumbs, setBreadcrumbs] = useState<Folder[]>([]);

  // UI states
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [newFolderDialogOpen, setNewFolderDialogOpen] = useState(false);
  const [requestDialogOpen, setRequestDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [contextMenuAnchor, setContextMenuAnchor] = useState<null | HTMLElement>(null);
  const [viewMode, setViewMode] = useState<'files' | 'requests'>('files');

  // Form states
  const [uploadFiles, setUploadFiles] = useState<FileList | null>(null);
  const [uploadCategory, setUploadCategory] = useState('financial');
  const [newFolderName, setNewFolderName] = useState('');

  // Fetch folders and documents
  const fetchContents = async (folderId: string | null = null) => {
    try {
      setLoading(true);
      const token = await getToken();

      const folderQuery = folderId ? `?folder_id=${folderId}` : '';

      // Fetch folders
      const foldersResponse = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/processes/${processId}/folders${folderQuery}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (foldersResponse.ok) {
        const foldersData = await foldersResponse.json();
        setFolders(foldersData);
      }

      // Fetch documents in current folder
      const docsResponse = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/processes/${processId}/documents${folderQuery}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (docsResponse.ok) {
        const docsData = await docsResponse.json();
        setDocuments(docsData);
      }

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching VDR contents:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch document requests
  const fetchDocumentRequests = async () => {
    try {
      const token = await getToken();
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/processes/${processId}/document-requests`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setDocumentRequests(data);
      }
    } catch (err) {
      console.error('Error fetching document requests:', err);
    }
  };

  useEffect(() => {
    fetchContents(currentFolderId);
    fetchDocumentRequests();
  }, [processId, currentFolderId]);

  // Handle folder navigation
  const handleFolderClick = (folder: Folder) => {
    setCurrentFolderId(folder.id);
    setBreadcrumbs([...breadcrumbs, folder]);
  };

  const handleBreadcrumbClick = (index: number) => {
    if (index === -1) {
      // Root
      setCurrentFolderId(null);
      setBreadcrumbs([]);
    } else {
      const folder = breadcrumbs[index];
      setCurrentFolderId(folder.id);
      setBreadcrumbs(breadcrumbs.slice(0, index + 1));
    }
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!uploadFiles) return;

    try {
      const token = await getToken();
      const formData = new FormData();

      Array.from(uploadFiles).forEach((file) => {
        formData.append('files', file);
      });

      formData.append('folder_id', currentFolderId || '');
      formData.append('category', uploadCategory);

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/processes/${processId}/documents/upload`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        }
      );

      if (!response.ok) throw new Error('Upload failed');

      setUploadDialogOpen(false);
      setUploadFiles(null);
      await fetchContents(currentFolderId);
    } catch (err) {
      console.error('Error uploading files:', err);
    }
  };

  // Handle folder creation
  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return;

    try {
      const token = await getToken();
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/processes/${processId}/folders`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: newFolderName,
            parent_id: currentFolderId,
          }),
        }
      );

      if (!response.ok) throw new Error('Failed to create folder');

      setNewFolderDialogOpen(false);
      setNewFolderName('');
      await fetchContents(currentFolderId);
    } catch (err) {
      console.error('Error creating folder:', err);
    }
  };

  // Handle document download
  const handleDownload = async (document: Document) => {
    try {
      const token = await getToken();
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/documents/${document.id}/download`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = document.filename;
        a.click();
      }
    } catch (err) {
      console.error('Error downloading document:', err);
    }
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  };

  // Get status color
  const getStatusColor = (status: string) => {
    const colors: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'error'> = {
      'pending': 'warning',
      'uploaded': 'primary',
      'under_review': 'info',
      'reviewed': 'success',
      'approved': 'success',
      'rejected': 'error',
    };
    return colors[status] || 'default';
  };

  // Render document requests view
  const renderDocumentRequests = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Request</TableCell>
            <TableCell>Category</TableCell>
            <TableCell>Priority</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Due Date</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {documentRequests.map((request) => (
            <TableRow key={request.id}>
              <TableCell>
                <Typography variant="body2" fontWeight="bold">
                  {request.title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {request.description}
                </Typography>
              </TableCell>
              <TableCell>
                <Chip label={request.category} size="small" />
              </TableCell>
              <TableCell>
                <Chip
                  label={request.priority}
                  size="small"
                  color={request.priority === 'high' ? 'error' : 'default'}
                />
              </TableCell>
              <TableCell>
                <Chip label={request.status} size="small" color={getStatusColor(request.status)} />
              </TableCell>
              <TableCell>{new Date(request.due_date).toLocaleDateString()}</TableCell>
              <TableCell>
                <Button size="small" variant="outlined">
                  Fulfill
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">Virtual Data Room</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant={viewMode === 'files' ? 'contained' : 'outlined'}
            onClick={() => setViewMode('files')}
          >
            Files & Folders
          </Button>
          <Button
            variant={viewMode === 'requests' ? 'contained' : 'outlined'}
            onClick={() => setViewMode('requests')}
          >
            Requests ({documentRequests.filter(r => r.status === 'pending').length})
          </Button>
        </Box>
      </Box>

      {viewMode === 'requests' ? (
        renderDocumentRequests()
      ) : (
        <Card>
          <CardContent>
            {/* Toolbar */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Breadcrumbs separator={<NavigateIcon fontSize="small" />}>
                <Link
                  component="button"
                  variant="body2"
                  onClick={() => handleBreadcrumbClick(-1)}
                  underline="hover"
                >
                  Root
                </Link>
                {breadcrumbs.map((folder, index) => (
                  <Link
                    key={folder.id}
                    component="button"
                    variant="body2"
                    onClick={() => handleBreadcrumbClick(index)}
                    underline="hover"
                  >
                    {folder.name}
                  </Link>
                ))}
              </Breadcrumbs>

              {!readOnly && (
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<NewFolderIcon />}
                    onClick={() => setNewFolderDialogOpen(true)}
                    size="small"
                  >
                    New Folder
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<UploadIcon />}
                    onClick={() => setUploadDialogOpen(true)}
                    size="small"
                  >
                    Upload
                  </Button>
                </Box>
              )}
            </Box>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            {loading && <LinearProgress sx={{ mb: 2 }} />}

            {/* Folders List */}
            {folders.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Folders
                </Typography>
                <List>
                  {folders.map((folder) => (
                    <ListItemButton
                      key={folder.id}
                      onClick={() => handleFolderClick(folder)}
                      sx={{ border: '1px solid #e0e0e0', borderRadius: 1, mb: 1 }}
                    >
                      <ListItemIcon>
                        <FolderIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={folder.name}
                        secondary={`${folder.document_count} documents`}
                      />
                    </ListItemButton>
                  ))}
                </List>
              </Box>
            )}

            {/* Documents Table */}
            {documents.length > 0 ? (
              <>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Documents
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Category</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Size</TableCell>
                        <TableCell>Uploaded</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {documents.map((doc) => (
                        <TableRow key={doc.id} hover>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <FileIcon fontSize="small" />
                              <Box>
                                <Typography variant="body2">{doc.title || doc.filename}</Typography>
                                {doc.is_confidential && (
                                  <Chip label="Confidential" size="small" color="error" sx={{ mt: 0.5 }} />
                                )}
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip label={doc.category} size="small" />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={doc.review_status}
                              size="small"
                              color={getStatusColor(doc.review_status)}
                            />
                          </TableCell>
                          <TableCell>{formatFileSize(doc.size)}</TableCell>
                          <TableCell>
                            <Typography variant="caption">
                              {new Date(doc.uploaded_at).toLocaleDateString()}
                            </Typography>
                            <Typography variant="caption" display="block" color="text.secondary">
                              by {doc.uploaded_by_name}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Tooltip title="Download">
                              <IconButton size="small" onClick={() => handleDownload(doc)}>
                                <DownloadIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="View">
                              <IconButton size="small">
                                <ViewIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            ) : !loading && folders.length === 0 && (
              <Alert severity="info">
                No documents in this folder. Upload documents to get started.
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Documents</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <input
              type="file"
              multiple
              onChange={(e) => setUploadFiles(e.target.files)}
              style={{ display: 'block', marginBottom: 16 }}
            />
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={uploadCategory}
                onChange={(e) => setUploadCategory(e.target.value)}
                label="Category"
              >
                <MenuItem value="financial">Financial</MenuItem>
                <MenuItem value="legal">Legal</MenuItem>
                <MenuItem value="operational">Operational</MenuItem>
                <MenuItem value="commercial">Commercial</MenuItem>
                <MenuItem value="hr">HR</MenuItem>
                <MenuItem value="it">IT</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleUpload} disabled={!uploadFiles}>
            Upload
          </Button>
        </DialogActions>
      </Dialog>

      {/* New Folder Dialog */}
      <Dialog open={newFolderDialogOpen} onClose={() => setNewFolderDialogOpen(false)}>
        <DialogTitle>Create New Folder</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Folder Name"
            fullWidth
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewFolderDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateFolder}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentRoom;
