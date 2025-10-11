/**
 * Document List Component with DataGrid
 * Story 3.2: Document List UI - Main component
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Chip,
  Menu,
  MenuItem,
  Button,
  TextField,
  InputAdornment,
  Select,
  FormControl,
  InputLabel,
  Stack,
  Checkbox,
  Alert,
  CircularProgress,
  Tooltip,
  SelectChangeEvent,
} from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridSelectionModel,
  GridToolbar,
} from '@mui/x-data-grid';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Archive as ArchiveIcon,
  DriveFileMove as MoveIcon,
  MoreVert as MoreVertIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  History as HistoryIcon,
  Share as ShareIcon,
  CloudUpload as UploadIcon,
  CreateNewFolder as NewFolderIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import {
  useGetDocumentsQuery,
  useDeleteDocumentMutation,
  useBulkOperationMutation,
  useGetDownloadUrlQuery,
  formatFileSize,
  getFileIcon,
  getDocumentTypeColor,
  Document,
  DocumentSearchParams,
} from '../api/documentsApi';

interface DocumentListProps {
  dealId?: string;
  folderPath?: string;
  onUploadClick?: () => void;
  onDocumentClick?: (document: Document) => void;
  onFolderClick?: (path: string) => void;
}

const DocumentList: React.FC<DocumentListProps> = ({
  dealId,
  folderPath = '/',
  onUploadClick,
  onDocumentClick,
  onFolderClick,
}) => {
  // State
  const [searchParams, setSearchParams] = useState<DocumentSearchParams>({
    deal_id: dealId,
    folder_path: folderPath,
    page: 1,
    per_page: 25,
    sort_by: 'uploaded_at',
    order: 'desc',
  });

  const [selectedDocuments, setSelectedDocuments] = useState<GridSelectionModel>([]);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [searchText, setSearchText] = useState('');
  const [documentTypeFilter, setDocumentTypeFilter] = useState<string>('');
  const [showConfidentialOnly, setShowConfidentialOnly] = useState(false);

  // RTK Query hooks
  const { data, isLoading, error } = useGetDocumentsQuery(searchParams);
  const [deleteDocument] = useDeleteDocumentMutation();
  const [bulkOperation] = useBulkOperationMutation();

  // Handlers
  const handleSearchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchText(event.target.value);
  }, []);

  const handleSearch = useCallback(() => {
    setSearchParams(prev => ({
      ...prev,
      search: searchText,
      page: 1,
    }));
  }, [searchText]);

  const handleDocumentTypeChange = useCallback((event: SelectChangeEvent) => {
    const value = event.target.value;
    setDocumentTypeFilter(value);
    setSearchParams(prev => ({
      ...prev,
      document_type: value || undefined,
      page: 1,
    }));
  }, []);

  const handleConfidentialToggle = useCallback(() => {
    setShowConfidentialOnly(prev => !prev);
    setSearchParams(prev => ({
      ...prev,
      is_confidential: !showConfidentialOnly || undefined,
      page: 1,
    }));
  }, [showConfidentialOnly]);

  const handleMenuOpen = useCallback((event: React.MouseEvent<HTMLElement>, document: Document) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedDocument(document);
  }, []);

  const handleMenuClose = useCallback(() => {
    setAnchorEl(null);
    setSelectedDocument(null);
  }, []);

  const handleDownload = useCallback(async (document: Document) => {
    if (document.presigned_url) {
      window.open(document.presigned_url, '_blank');
    }
    handleMenuClose();
  }, [handleMenuClose]);

  const handleDelete = useCallback(async (document: Document) => {
    if (window.confirm(`Delete ${document.filename}?`)) {
      await deleteDocument(document.id);
    }
    handleMenuClose();
  }, [deleteDocument, handleMenuClose]);

  const handleBulkDelete = useCallback(async () => {
    if (selectedDocuments.length === 0) return;

    if (window.confirm(`Delete ${selectedDocuments.length} documents?`)) {
      await bulkOperation({
        operation: 'delete',
        document_ids: selectedDocuments as string[],
      });
      setSelectedDocuments([]);
    }
  }, [selectedDocuments, bulkOperation]);

  const handleBulkArchive = useCallback(async () => {
    if (selectedDocuments.length === 0) return;

    await bulkOperation({
      operation: 'archive',
      document_ids: selectedDocuments as string[],
    });
    setSelectedDocuments([]);
  }, [selectedDocuments, bulkOperation]);

  const handleView = useCallback((document: Document) => {
    if (onDocumentClick) {
      onDocumentClick(document);
    }
    handleMenuClose();
  }, [onDocumentClick, handleMenuClose]);

  // Columns definition
  const columns: GridColDef[] = useMemo(() => [
    {
      field: 'icon',
      headerName: '',
      width: 50,
      sortable: false,
      renderCell: (params: GridRenderCellParams<Document>) => (
        <Icon
          name={getFileIcon(params.row.mime_type, params.row.file_extension)}
          color={getDocumentTypeColor(params.row.document_type)}
        />
      ),
    },
    {
      field: 'filename',
      headerName: 'Name',
      flex: 1,
      minWidth: 200,
      renderCell: (params: GridRenderCellParams<Document>) => (
        <Box>
          <Typography
            variant="body2"
            sx={{
              fontWeight: 500,
              cursor: 'pointer',
              '&:hover': { textDecoration: 'underline' },
            }}
            onClick={() => handleView(params.row)}
          >
            {params.row.title || params.row.original_filename}
          </Typography>
          {params.row.description && (
            <Typography variant="caption" color="text.secondary">
              {params.row.description}
            </Typography>
          )}
        </Box>
      ),
    },
    {
      field: 'document_type',
      headerName: 'Type',
      width: 120,
      renderCell: (params: GridRenderCellParams<Document>) => (
        <Chip
          label={params.row.document_type.replace('_', ' ')}
          size="small"
          sx={{
            bgcolor: getDocumentTypeColor(params.row.document_type) + '20',
            color: getDocumentTypeColor(params.row.document_type),
          }}
        />
      ),
    },
    {
      field: 'file_size',
      headerName: 'Size',
      width: 100,
      valueFormatter: ({ value }) => formatFileSize(value as number),
    },
    {
      field: 'uploaded_at',
      headerName: 'Uploaded',
      width: 150,
      valueFormatter: ({ value }) => format(new Date(value as string), 'MMM d, yyyy'),
    },
    {
      field: 'tags',
      headerName: 'Tags',
      width: 200,
      renderCell: (params: GridRenderCellParams<Document>) => (
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
          {params.row.tags.slice(0, 2).map((tag, index) => (
            <Chip key={index} label={tag} size="small" variant="outlined" />
          ))}
          {params.row.tags.length > 2 && (
            <Chip label={`+${params.row.tags.length - 2}`} size="small" variant="outlined" />
          )}
        </Box>
      ),
    },
    {
      field: 'is_confidential',
      headerName: 'Access',
      width: 100,
      renderCell: (params: GridRenderCellParams<Document>) => (
        <Chip
          label={params.row.is_confidential ? 'Confidential' : 'Public'}
          size="small"
          color={params.row.is_confidential ? 'warning' : 'default'}
          variant="outlined"
        />
      ),
    },
    {
      field: 'actions',
      headerName: '',
      width: 50,
      sortable: false,
      renderCell: (params: GridRenderCellParams<Document>) => (
        <IconButton
          size="small"
          onClick={(e) => handleMenuOpen(e, params.row)}
        >
          <MoreVertIcon fontSize="small" />
        </IconButton>
      ),
    },
  ], [handleView, handleMenuOpen]);

  // Loading and error states
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Error loading documents. Please try again later.
      </Alert>
    );
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <TextField
            size="small"
            placeholder="Search documents..."
            value={searchText}
            onChange={handleSearchChange}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
            sx={{ flexGrow: 1, maxWidth: 400 }}
          />

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Document Type</InputLabel>
            <Select
              value={documentTypeFilter}
              onChange={handleDocumentTypeChange}
              label="Document Type"
            >
              <MenuItem value="">All Types</MenuItem>
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

          <Button
            variant={showConfidentialOnly ? 'contained' : 'outlined'}
            size="small"
            onClick={handleConfidentialToggle}
            startIcon={<FilterIcon />}
          >
            Confidential
          </Button>

          <Box sx={{ flexGrow: 1 }} />

          {selectedDocuments.length > 0 && (
            <>
              <Button
                size="small"
                startIcon={<ArchiveIcon />}
                onClick={handleBulkArchive}
              >
                Archive ({selectedDocuments.length})
              </Button>
              <Button
                size="small"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={handleBulkDelete}
              >
                Delete ({selectedDocuments.length})
              </Button>
            </>
          )}

          <Button
            variant="contained"
            startIcon={<UploadIcon />}
            onClick={onUploadClick}
          >
            Upload
          </Button>

          <Button
            variant="outlined"
            startIcon={<NewFolderIcon />}
            onClick={() => onFolderClick?.('new')}
          >
            New Folder
          </Button>
        </Stack>
      </Paper>

      {/* Document Grid */}
      <Paper sx={{ flexGrow: 1, overflow: 'hidden' }}>
        <DataGrid
          rows={data?.data || []}
          columns={columns}
          pageSize={searchParams.per_page || 25}
          rowsPerPageOptions={[10, 25, 50, 100]}
          checkboxSelection
          disableSelectionOnClick
          selectionModel={selectedDocuments}
          onSelectionModelChange={setSelectedDocuments}
          pagination
          paginationMode="server"
          rowCount={data?.pagination.total || 0}
          page={(searchParams.page || 1) - 1}
          onPageChange={(page) => setSearchParams(prev => ({ ...prev, page: page + 1 }))}
          onPageSizeChange={(pageSize) => setSearchParams(prev => ({ ...prev, per_page: pageSize }))}
          loading={isLoading}
          components={{
            Toolbar: GridToolbar,
          }}
          sx={{
            '& .MuiDataGrid-row': {
              cursor: 'pointer',
            },
          }}
        />
      </Paper>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => selectedDocument && handleView(selectedDocument)}>
          <ViewIcon fontSize="small" sx={{ mr: 1 }} />
          View
        </MenuItem>
        <MenuItem onClick={() => selectedDocument && handleDownload(selectedDocument)}>
          <DownloadIcon fontSize="small" sx={{ mr: 1 }} />
          Download
        </MenuItem>
        <MenuItem onClick={() => console.log('Edit', selectedDocument)}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <MenuItem onClick={() => console.log('Share', selectedDocument)}>
          <ShareIcon fontSize="small" sx={{ mr: 1 }} />
          Share
        </MenuItem>
        <MenuItem onClick={() => console.log('Version History', selectedDocument)}>
          <HistoryIcon fontSize="small" sx={{ mr: 1 }} />
          Version History
        </MenuItem>
        <MenuItem onClick={() => console.log('Move', selectedDocument)}>
          <MoveIcon fontSize="small" sx={{ mr: 1 }} />
          Move
        </MenuItem>
        <MenuItem
          onClick={() => selectedDocument && handleDelete(selectedDocument)}
          sx={{ color: 'error.main' }}
        >
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>
    </Box>
  );
};

// Icon component helper
const Icon: React.FC<{ name: string; color: string }> = ({ name, color }) => {
  const icons: Record<string, any> = {
    image: '🖼️',
    movie: '🎬',
    picture_as_pdf: '📄',
    description: '📝',
    table_chart: '📊',
    slideshow: '📽️',
    folder_zip: '🗂️',
    insert_drive_file: '📎',
  };

  return (
    <Box
      sx={{
        width: 32,
        height: 32,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 1,
        bgcolor: color + '20',
        fontSize: '1.2rem',
      }}
    >
      {icons[name] || icons.insert_drive_file}
    </Box>
  );
};

export default DocumentList;