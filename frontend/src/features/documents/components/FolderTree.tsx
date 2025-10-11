/**
 * Folder Tree Component for Document Organization
 * Story 3.4: Folder Organization - Hierarchical folder navigation
 */

import React, { useState, useCallback } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  IconButton,
  Typography,
  Menu,
  MenuItem,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Folder as FolderIcon,
  FolderOpen as FolderOpenIcon,
  ExpandMore as ExpandIcon,
  ChevronRight as CollapseIcon,
  CreateNewFolder as NewFolderIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreIcon,
  Home as HomeIcon,
  Lock as LockIcon,
} from '@mui/icons-material';
import {
  useGetFoldersQuery,
  useCreateFolderMutation,
  useUpdateFolderMutation,
  useDeleteFolderMutation,
  Folder,
} from '../api/documentsApi';

interface FolderTreeProps {
  dealId?: string;
  selectedPath: string;
  onFolderSelect: (path: string) => void;
  onRefresh?: () => void;
}

interface FolderNodeProps {
  folder: Folder;
  level: number;
  selectedPath: string;
  onSelect: (path: string) => void;
  onEdit: (folder: Folder) => void;
  onDelete: (folder: Folder) => void;
  onNewFolder: (parentPath: string) => void;
}

const FolderNode: React.FC<FolderNodeProps> = ({
  folder,
  level,
  selectedPath,
  onSelect,
  onEdit,
  onDelete,
  onNewFolder,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const { data: subfolders, isLoading } = useGetFoldersQuery(
    { path: folder.path },
    { skip: !expanded }
  );

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setExpanded(!expanded);
  };

  const handleMenuOpen = (e: React.MouseEvent<HTMLElement>) => {
    e.stopPropagation();
    setAnchorEl(e.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleEdit = () => {
    onEdit(folder);
    handleMenuClose();
  };

  const handleDelete = () => {
    onDelete(folder);
    handleMenuClose();
  };

  const handleNewSubfolder = () => {
    onNewFolder(folder.path);
    handleMenuClose();
    setExpanded(true);
  };

  const isSelected = selectedPath === folder.path;

  return (
    <>
      <ListItem
        disablePadding
        sx={{ pl: level * 2 }}
        secondaryAction={
          !folder.is_system_folder && (
            <IconButton edge="end" size="small" onClick={handleMenuOpen}>
              <MoreIcon fontSize="small" />
            </IconButton>
          )
        }
      >
        <ListItemButton
          selected={isSelected}
          onClick={() => onSelect(folder.path)}
        >
          {subfolders && subfolders.length > 0 && (
            <IconButton size="small" onClick={handleToggle} sx={{ mr: 0.5 }}>
              {expanded ? <ExpandIcon /> : <CollapseIcon />}
            </IconButton>
          )}
          <ListItemIcon sx={{ minWidth: 40 }}>
            {folder.is_system_folder ? (
              <LockIcon color="action" />
            ) : expanded ? (
              <FolderOpenIcon sx={{ color: folder.color || 'inherit' }} />
            ) : (
              <FolderIcon sx={{ color: folder.color || 'inherit' }} />
            )}
          </ListItemIcon>
          <ListItemText
            primary={folder.name}
            secondary={
              folder.document_count > 0 ? `${folder.document_count} files` : null
            }
          />
        </ListItemButton>
      </ListItem>

      {/* Subfolders */}
      {expanded && (
        <Collapse in={expanded}>
          {isLoading ? (
            <Box display="flex" justifyContent="center" p={2}>
              <CircularProgress size={20} />
            </Box>
          ) : (
            <List disablePadding>
              {subfolders?.map((subfolder) => (
                <FolderNode
                  key={subfolder.id}
                  folder={subfolder}
                  level={level + 1}
                  selectedPath={selectedPath}
                  onSelect={onSelect}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  onNewFolder={onNewFolder}
                />
              ))}
            </List>
          )}
        </Collapse>
      )}

      {/* Context menu */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={handleNewSubfolder}>
          <NewFolderIcon fontSize="small" sx={{ mr: 1 }} />
          New Subfolder
        </MenuItem>
        {!folder.is_readonly && (
          <>
            <MenuItem onClick={handleEdit}>
              <EditIcon fontSize="small" sx={{ mr: 1 }} />
              Rename
            </MenuItem>
            <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
              <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
              Delete
            </MenuItem>
          </>
        )}
      </Menu>
    </>
  );
};

const FolderTree: React.FC<FolderTreeProps> = ({
  dealId,
  selectedPath,
  onFolderSelect,
  onRefresh,
}) => {
  const [newFolderDialog, setNewFolderDialog] = useState<{
    open: boolean;
    parentPath: string;
  }>({ open: false, parentPath: '/' });
  const [editFolderDialog, setEditFolderDialog] = useState<{
    open: boolean;
    folder: Folder | null;
  }>({ open: false, folder: null });
  const [folderName, setFolderName] = useState('');
  const [folderDescription, setFolderDescription] = useState('');

  // RTK Query hooks
  const { data: rootFolders, isLoading, error } = useGetFoldersQuery({
    path: '/',
    deal_id: dealId,
  });
  const [createFolder] = useCreateFolderMutation();
  const [updateFolder] = useUpdateFolderMutation();
  const [deleteFolder] = useDeleteFolderMutation();

  // Handlers
  const handleNewFolder = useCallback((parentPath: string) => {
    setNewFolderDialog({ open: true, parentPath });
    setFolderName('');
    setFolderDescription('');
  }, []);

  const handleEditFolder = useCallback((folder: Folder) => {
    setEditFolderDialog({ open: true, folder });
    setFolderName(folder.name);
    setFolderDescription(folder.description || '');
  }, []);

  const handleDeleteFolder = useCallback(
    async (folder: Folder) => {
      if (
        window.confirm(
          `Delete folder "${folder.name}"? This will also delete all subfolders and move documents to the parent folder.`
        )
      ) {
        try {
          await deleteFolder(folder.id).unwrap();
          if (onRefresh) onRefresh();
        } catch (error) {
          console.error('Failed to delete folder:', error);
        }
      }
    },
    [deleteFolder, onRefresh]
  );

  const handleCreateFolder = async () => {
    if (!folderName.trim()) return;

    try {
      await createFolder({
        name: folderName,
        parent_path: newFolderDialog.parentPath,
        description: folderDescription,
        deal_id: dealId,
      }).unwrap();

      setNewFolderDialog({ open: false, parentPath: '/' });
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error('Failed to create folder:', error);
    }
  };

  const handleUpdateFolder = async () => {
    if (!editFolderDialog.folder || !folderName.trim()) return;

    try {
      await updateFolder({
        id: editFolderDialog.folder.id,
        data: {
          name: folderName,
          description: folderDescription,
        },
      }).unwrap();

      setEditFolderDialog({ open: false, folder: null });
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error('Failed to update folder:', error);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Failed to load folders
      </Alert>
    );
  }

  return (
    <>
      <Box sx={{ width: '100%', maxWidth: 360 }}>
        <Box
          sx={{
            p: 2,
            borderBottom: 1,
            borderColor: 'divider',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Typography variant="subtitle1" fontWeight="medium">
            Folders
          </Typography>
          <IconButton size="small" onClick={() => handleNewFolder('/')}>
            <NewFolderIcon />
          </IconButton>
        </Box>

        <List>
          {/* Root folder */}
          <ListItem disablePadding>
            <ListItemButton
              selected={selectedPath === '/'}
              onClick={() => onFolderSelect('/')}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                <HomeIcon />
              </ListItemIcon>
              <ListItemText primary="All Documents" />
            </ListItemButton>
          </ListItem>

          {/* System folders */}
          {rootFolders
            ?.filter((f) => f.is_system_folder)
            .map((folder) => (
              <FolderNode
                key={folder.id}
                folder={folder}
                level={1}
                selectedPath={selectedPath}
                onSelect={onFolderSelect}
                onEdit={handleEditFolder}
                onDelete={handleDeleteFolder}
                onNewFolder={handleNewFolder}
              />
            ))}

          {/* User folders */}
          {rootFolders
            ?.filter((f) => !f.is_system_folder)
            .map((folder) => (
              <FolderNode
                key={folder.id}
                folder={folder}
                level={1}
                selectedPath={selectedPath}
                onSelect={onFolderSelect}
                onEdit={handleEditFolder}
                onDelete={handleDeleteFolder}
                onNewFolder={handleNewFolder}
              />
            ))}
        </List>
      </Box>

      {/* New Folder Dialog */}
      <Dialog
        open={newFolderDialog.open}
        onClose={() => setNewFolderDialog({ open: false, parentPath: '/' })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create New Folder</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Folder Name"
            fullWidth
            variant="outlined"
            value={folderName}
            onChange={(e) => setFolderName(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description (optional)"
            fullWidth
            variant="outlined"
            multiline
            rows={3}
            value={folderDescription}
            onChange={(e) => setFolderDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewFolderDialog({ open: false, parentPath: '/' })}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateFolder}
            variant="contained"
            disabled={!folderName.trim()}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Folder Dialog */}
      <Dialog
        open={editFolderDialog.open}
        onClose={() => setEditFolderDialog({ open: false, folder: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Folder</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Folder Name"
            fullWidth
            variant="outlined"
            value={folderName}
            onChange={(e) => setFolderName(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description (optional)"
            fullWidth
            variant="outlined"
            multiline
            rows={3}
            value={folderDescription}
            onChange={(e) => setFolderDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditFolderDialog({ open: false, folder: null })}>
            Cancel
          </Button>
          <Button
            onClick={handleUpdateFolder}
            variant="contained"
            disabled={!folderName.trim()}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default FolderTree;