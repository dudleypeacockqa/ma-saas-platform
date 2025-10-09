/**
 * Due Diligence Checklist Component
 * Interactive checklist management for DD processes
 * Supports item tracking, status updates, document linking, and progress monitoring
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Checkbox,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  LinearProgress,
  Alert,
  Tooltip,
  Badge,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
} from '@mui/material';
import {
  ExpandMore as ExpandIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as UncheckedIcon,
  AttachFile as AttachIcon,
  Comment as CommentIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Flag as FlagIcon,
} from '@mui/icons-material';

interface DDChecklistProps {
  processId: string;
  checklistId: string;
  readOnly?: boolean;
}

interface ChecklistItem {
  id: string;
  category: string;
  title: string;
  description: string;
  status: string;
  is_required: boolean;
  is_critical: boolean;
  assigned_to: string | null;
  assigned_to_name: string | null;
  due_date: string | null;
  completed_at: string | null;
  completed_by: string | null;
  documents_count: number;
  comments_count: number;
  risk_level: string;
  validation_result: string | null;
  notes: string;
  order_index: number;
}

interface CategoryGroup {
  category: string;
  items: ChecklistItem[];
  completed: number;
  total: number;
  progress: number;
}

const DDChecklist: React.FC<DDChecklistProps> = ({
  processId,
  checklistId,
  readOnly = false,
}) => {
  const { getToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [items, setItems] = useState<ChecklistItem[]>([]);
  const [categories, setCategories] = useState<CategoryGroup[]>([]);
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<ChecklistItem | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [commentDialogOpen, setCommentDialogOpen] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterCategory, setFilterCategory] = useState<string>('all');

  // Fetch checklist items
  const fetchChecklistItems = async () => {
    try {
      setLoading(true);
      const token = await getToken();

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/processes/${processId}/items`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) throw new Error('Failed to fetch checklist items');

      const data = await response.json();
      setItems(data);

      // Group by category
      groupItemsByCategory(data);

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching checklist items:', err);
    } finally {
      setLoading(false);
    }
  };

  // Group items by category
  const groupItemsByCategory = (itemsList: ChecklistItem[]) => {
    const grouped = itemsList.reduce((acc, item) => {
      if (!acc[item.category]) {
        acc[item.category] = [];
      }
      acc[item.category].push(item);
      return acc;
    }, {} as Record<string, ChecklistItem[]>);

    const categoryGroups: CategoryGroup[] = Object.entries(grouped).map(([category, categoryItems]) => {
      const completed = categoryItems.filter(item => item.status === 'completed').length;
      const total = categoryItems.length;
      return {
        category,
        items: categoryItems.sort((a, b) => a.order_index - b.order_index),
        completed,
        total,
        progress: total > 0 ? (completed / total) * 100 : 0,
      };
    });

    setCategories(categoryGroups);
  };

  useEffect(() => {
    fetchChecklistItems();
  }, [processId, checklistId]);

  // Toggle item completion
  const toggleItemStatus = async (item: ChecklistItem) => {
    if (readOnly) return;

    try {
      const token = await getToken();
      const newStatus = item.status === 'completed' ? 'pending' : 'completed';

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/due-diligence/items/${item.id}/status`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (!response.ok) throw new Error('Failed to update item status');

      // Refresh items
      await fetchChecklistItems();
    } catch (err) {
      console.error('Error updating item status:', err);
    }
  };

  // Handle item click
  const handleItemClick = (item: ChecklistItem) => {
    setSelectedItem(item);
    setDetailsDialogOpen(true);
  };

  // Get category icon color
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'financial': '#1976d2',
      'legal': '#7b1fa2',
      'operational': '#388e3c',
      'commercial': '#f57c00',
      'hr': '#c2185b',
      'it': '#0288d1',
      'environmental': '#689f38',
      'ip': '#5d4037',
      'regulatory': '#d32f2f',
      'tax': '#303f9f',
    };
    return colors[category.toLowerCase()] || '#757575';
  };

  // Get status color
  const getStatusColor = (status: string): 'default' | 'primary' | 'success' | 'warning' | 'error' => {
    const colors: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'error'> = {
      'pending': 'default',
      'in_progress': 'primary',
      'under_review': 'warning',
      'completed': 'success',
      'blocked': 'error',
    };
    return colors[status] || 'default';
  };

  // Render category accordion
  const renderCategoryAccordion = (categoryGroup: CategoryGroup) => {
    const filteredItems = categoryGroup.items.filter(item => {
      if (filterStatus !== 'all' && item.status !== filterStatus) return false;
      return true;
    });

    if (filteredItems.length === 0) return null;

    return (
      <Accordion
        key={categoryGroup.category}
        expanded={expandedCategory === categoryGroup.category}
        onChange={() => setExpandedCategory(
          expandedCategory === categoryGroup.category ? null : categoryGroup.category
        )}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
            <Box
              sx={{
                width: 4,
                height: 40,
                bgcolor: getCategoryColor(categoryGroup.category),
                borderRadius: 1,
              }}
            />
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                {categoryGroup.category.replace('_', ' ')}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  {categoryGroup.completed}/{categoryGroup.total} completed
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={categoryGroup.progress}
                  sx={{ width: 200, height: 6, borderRadius: 3 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {categoryGroup.progress.toFixed(0)}%
                </Typography>
              </Box>
            </Box>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <List>
            {filteredItems.map((item) => (
              <ListItem
                key={item.id}
                sx={{
                  border: '1px solid #e0e0e0',
                  borderRadius: 1,
                  mb: 1,
                  bgcolor: item.status === 'completed' ? '#f5f5f5' : 'white',
                }}
                secondaryAction={
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {item.documents_count > 0 && (
                      <Badge badgeContent={item.documents_count} color="primary">
                        <AttachIcon fontSize="small" />
                      </Badge>
                    )}
                    {item.comments_count > 0 && (
                      <Badge badgeContent={item.comments_count} color="secondary">
                        <CommentIcon fontSize="small" />
                      </Badge>
                    )}
                    {item.is_critical && (
                      <Tooltip title="Critical Item">
                        <FlagIcon fontSize="small" color="error" />
                      </Tooltip>
                    )}
                  </Box>
                }
              >
                <ListItemIcon>
                  <Checkbox
                    edge="start"
                    checked={item.status === 'completed'}
                    onChange={() => toggleItemStatus(item)}
                    disabled={readOnly}
                    icon={<UncheckedIcon />}
                    checkedIcon={<CheckCircleIcon />}
                  />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography
                        variant="body1"
                        sx={{
                          textDecoration: item.status === 'completed' ? 'line-through' : 'none',
                          cursor: 'pointer',
                        }}
                        onClick={() => handleItemClick(item)}
                      >
                        {item.title}
                      </Typography>
                      {item.is_required && (
                        <Chip label="Required" size="small" color="error" variant="outlined" />
                      )}
                      <Chip
                        label={item.status}
                        size="small"
                        color={getStatusColor(item.status)}
                      />
                    </Box>
                  }
                  secondary={
                    <Box sx={{ mt: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        {item.description}
                      </Typography>
                      {item.assigned_to_name && (
                        <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                          Assigned to: {item.assigned_to_name}
                        </Typography>
                      )}
                      {item.due_date && (
                        <Typography variant="caption" display="block">
                          Due: {new Date(item.due_date).toLocaleDateString()}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </AccordionDetails>
      </Accordion>
    );
  };

  // Calculate overall progress
  const calculateOverallProgress = () => {
    if (categories.length === 0) return 0;
    const total = categories.reduce((sum, cat) => sum + cat.total, 0);
    const completed = categories.reduce((sum, cat) => sum + cat.completed, 0);
    return total > 0 ? (completed / total) * 100 : 0;
  };

  return (
    <Box>
      {/* Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5">Due Diligence Checklist</Typography>
            {!readOnly && (
              <Button variant="outlined" startIcon={<AddIcon />} size="small">
                Add Item
              </Button>
            )}
          </Box>

          {/* Overall Progress */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Overall Progress
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {calculateOverallProgress().toFixed(0)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={calculateOverallProgress()}
              sx={{ height: 10, borderRadius: 5 }}
            />
          </Box>

          {/* Filters */}
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Filter by Status</InputLabel>
                <Select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  label="Filter by Status"
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="under_review">Under Review</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="blocked">Blocked</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Category Accordions */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <Typography>Loading checklist...</Typography>
        </Box>
      ) : (
        categories.map(renderCategoryAccordion)
      )}

      {/* Item Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedItem && (
          <>
            <DialogTitle>{selectedItem.title}</DialogTitle>
            <DialogContent>
              <Typography variant="body2" paragraph>
                {selectedItem.description}
              </Typography>

              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">Status</Typography>
                  <Typography variant="body2">
                    <Chip
                      label={selectedItem.status}
                      color={getStatusColor(selectedItem.status)}
                      size="small"
                    />
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">Category</Typography>
                  <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                    {selectedItem.category.replace('_', ' ')}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">Assigned To</Typography>
                  <Typography variant="body2">
                    {selectedItem.assigned_to_name || 'Unassigned'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">Due Date</Typography>
                  <Typography variant="body2">
                    {selectedItem.due_date
                      ? new Date(selectedItem.due_date).toLocaleDateString()
                      : 'No due date'}
                  </Typography>
                </Grid>
              </Grid>

              {selectedItem.notes && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary">Notes</Typography>
                  <Typography variant="body2">{selectedItem.notes}</Typography>
                </Box>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
              {!readOnly && (
                <Button variant="contained">Edit Item</Button>
              )}
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default DDChecklist;
