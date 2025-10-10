import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  TrendingUp,
  DollarSign,
  Building2,
  Star,
  Eye,
  Phone,
  MessageSquare,
  CheckCircle,
  X,
  ArrowRight,
  MoreVertical
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';

interface Opportunity {
  id: string;
  company_name: string;
  region: string;
  industry_vertical: string;
  status: OpportunityStatus;
  overall_score?: number;
  annual_revenue?: number;
  ebitda?: number;
  created_at: string;
}

enum OpportunityStatus {
  NEW = 'new',
  SCREENING = 'screening',
  QUALIFIED = 'qualified',
  CONTACTED = 'contacted',
  IN_DISCUSSION = 'in_discussion',
  REJECTED = 'rejected',
  CONVERTED_TO_DEAL = 'converted_to_deal'
}

interface PipelineColumn {
  status: OpportunityStatus;
  title: string;
  icon: React.ReactNode;
  color: string;
}

const columns: PipelineColumn[] = [
  {
    status: OpportunityStatus.NEW,
    title: 'New Leads',
    icon: <Star className="w-4 h-4" />,
    color: 'border-blue-300 bg-blue-50'
  },
  {
    status: OpportunityStatus.SCREENING,
    title: 'Screening',
    icon: <Eye className="w-4 h-4" />,
    color: 'border-yellow-300 bg-yellow-50'
  },
  {
    status: OpportunityStatus.QUALIFIED,
    title: 'Qualified',
    icon: <CheckCircle className="w-4 h-4" />,
    color: 'border-green-300 bg-green-50'
  },
  {
    status: OpportunityStatus.CONTACTED,
    title: 'Contacted',
    icon: <Phone className="w-4 h-4" />,
    color: 'border-purple-300 bg-purple-50'
  },
  {
    status: OpportunityStatus.IN_DISCUSSION,
    title: 'In Discussion',
    icon: <MessageSquare className="w-4 h-4" />,
    color: 'border-indigo-300 bg-indigo-50'
  },
  {
    status: OpportunityStatus.CONVERTED_TO_DEAL,
    title: 'Converted',
    icon: <TrendingUp className="w-4 h-4" />,
    color: 'border-emerald-300 bg-emerald-50'
  }
];

interface SortableOpportunityCardProps {
  opportunity: Opportunity;
  onConvertToDeal: (id: string) => void;
  onReject: (id: string) => void;
}

const SortableOpportunityCard: React.FC<SortableOpportunityCardProps> = ({
  opportunity,
  onConvertToDeal,
  onReject
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging
  } = useSortable({ id: opportunity.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1
  };

  const formatCurrency = (amount?: number) => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(amount);
  };

  const getScoreColor = (score?: number) => {
    if (!score) return 'text-gray-400';
    if (score >= 75) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Card
      ref={setNodeRef}
      style={style}
      className="mb-3 hover:shadow-md transition-shadow cursor-move"
      {...attributes}
      {...listeners}
    >
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1">
            <h4 className="font-semibold text-sm mb-1">{opportunity.company_name}</h4>
            <p className="text-xs text-gray-500">
              {opportunity.region} • {opportunity.industry_vertical}
            </p>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
              <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                <MoreVertical className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {opportunity.status === OpportunityStatus.QUALIFIED ||
               opportunity.status === OpportunityStatus.IN_DISCUSSION ? (
                <DropdownMenuItem onClick={() => onConvertToDeal(opportunity.id)}>
                  <ArrowRight className="w-4 h-4 mr-2" />
                  Convert to Deal
                </DropdownMenuItem>
              ) : null}
              <DropdownMenuItem onClick={() => onReject(opportunity.id)} className="text-red-600">
                <X className="w-4 h-4 mr-2" />
                Reject
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Score */}
        {opportunity.overall_score !== undefined && (
          <div className="mb-3">
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs text-gray-500">Score</span>
              <span className={`text-sm font-bold ${getScoreColor(opportunity.overall_score)}`}>
                {opportunity.overall_score.toFixed(0)}/100
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div
                className={`h-1.5 rounded-full ${
                  opportunity.overall_score >= 75 ? 'bg-green-500' :
                  opportunity.overall_score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${opportunity.overall_score}%` }}
              />
            </div>
          </div>
        )}

        {/* Financials */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <p className="text-gray-500">Revenue</p>
            <p className="font-semibold flex items-center">
              <DollarSign className="w-3 h-3 mr-1" />
              {formatCurrency(opportunity.annual_revenue)}
            </p>
          </div>
          <div>
            <p className="text-gray-500">EBITDA</p>
            <p className="font-semibold flex items-center">
              <DollarSign className="w-3 h-3 mr-1" />
              {formatCurrency(opportunity.ebitda)}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export const DealPipeline: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Record<OpportunityStatus, Opportunity[]>>({
    [OpportunityStatus.NEW]: [],
    [OpportunityStatus.SCREENING]: [],
    [OpportunityStatus.QUALIFIED]: [],
    [OpportunityStatus.CONTACTED]: [],
    [OpportunityStatus.IN_DISCUSSION]: [],
    [OpportunityStatus.REJECTED]: [],
    [OpportunityStatus.CONVERTED_TO_DEAL]: []
  });

  const [loading, setLoading] = useState(true);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates
    })
  );

  useEffect(() => {
    fetchOpportunities();
  }, []);

  const fetchOpportunities = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/opportunities?limit=200', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data: Opportunity[] = await response.json();

        // Group by status
        const grouped: Record<OpportunityStatus, Opportunity[]> = {
          [OpportunityStatus.NEW]: [],
          [OpportunityStatus.SCREENING]: [],
          [OpportunityStatus.QUALIFIED]: [],
          [OpportunityStatus.CONTACTED]: [],
          [OpportunityStatus.IN_DISCUSSION]: [],
          [OpportunityStatus.REJECTED]: [],
          [OpportunityStatus.CONVERTED_TO_DEAL]: []
        };

        data.forEach(opp => {
          if (grouped[opp.status]) {
            grouped[opp.status].push(opp);
          }
        });

        setOpportunities(grouped);
      }
    } catch (error) {
      console.error('Error fetching opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    // Find which column the item is being dragged to
    const targetStatus = columns.find(col =>
      overId.startsWith(col.status)
    )?.status;

    if (!targetStatus) return;

    // Find the opportunity being dragged
    let draggedOpp: Opportunity | null = null;
    let sourceStatus: OpportunityStatus | null = null;

    for (const [status, opps] of Object.entries(opportunities)) {
      const found = opps.find(o => o.id === activeId);
      if (found) {
        draggedOpp = found;
        sourceStatus = status as OpportunityStatus;
        break;
      }
    }

    if (!draggedOpp || !sourceStatus || sourceStatus === targetStatus) return;

    // Optimistic update
    const newOpportunities = { ...opportunities };
    newOpportunities[sourceStatus] = newOpportunities[sourceStatus].filter(o => o.id !== activeId);
    newOpportunities[targetStatus] = [...newOpportunities[targetStatus], { ...draggedOpp, status: targetStatus }];
    setOpportunities(newOpportunities);

    // Update on server
    try {
      await fetch(`/api/opportunities/${activeId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: targetStatus })
      });
    } catch (error) {
      console.error('Error updating opportunity status:', error);
      // Revert on error
      fetchOpportunities();
    }
  };

  const convertToDeal = async (opportunityId: string) => {
    try {
      const response = await fetch(`/api/opportunities/${opportunityId}/convert-to-deal`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Opportunity converted to deal: ${result.deal_id}`);
        fetchOpportunities();
      }
    } catch (error) {
      console.error('Error converting to deal:', error);
      alert('Error converting opportunity to deal');
    }
  };

  const rejectOpportunity = async (opportunityId: string) => {
    try {
      await fetch(`/api/opportunities/${opportunityId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: OpportunityStatus.REJECTED })
      });

      fetchOpportunities();
    } catch (error) {
      console.error('Error rejecting opportunity:', error);
    }
  };

  const getTotalValue = (opps: Opportunity[]) => {
    return opps.reduce((sum, opp) => sum + (opp.annual_revenue || 0), 0);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center py-12">
          <Building2 className="w-12 h-12 mx-auto text-gray-300 animate-pulse" />
          <p className="mt-4 text-gray-500">Loading pipeline...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold">M&A Pipeline</h1>
        <p className="text-gray-500">Drag and drop opportunities through your pipeline</p>
      </div>

      {/* Pipeline Columns */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {columns.map((column) => {
            const columnOpps = opportunities[column.status] || [];
            const totalValue = getTotalValue(columnOpps);

            return (
              <div key={column.status} className="flex flex-col">
                <Card className={`border-t-4 ${column.color} mb-3`}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {column.icon}
                        <CardTitle className="text-sm font-semibold">
                          {column.title}
                        </CardTitle>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {columnOpps.length}
                      </Badge>
                    </div>
                    {totalValue > 0 && (
                      <p className="text-xs text-gray-500 mt-1">
                        {formatCurrency(totalValue)} total revenue
                      </p>
                    )}
                  </CardHeader>
                </Card>

                <SortableContext
                  items={columnOpps.map(o => o.id)}
                  strategy={verticalListSortingStrategy}
                  id={`${column.status}-droppable`}
                >
                  <div className="flex-1 min-h-[200px]">
                    {columnOpps.map((opp) => (
                      <SortableOpportunityCard
                        key={opp.id}
                        opportunity={opp}
                        onConvertToDeal={convertToDeal}
                        onReject={rejectOpportunity}
                      />
                    ))}
                  </div>
                </SortableContext>
              </div>
            );
          })}
        </div>
      </DndContext>

      {/* Pipeline Metrics */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Pipeline Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {columns.map((column) => {
              const columnOpps = opportunities[column.status] || [];
              const avgScore = columnOpps.reduce((sum, opp) => sum + (opp.overall_score || 0), 0) / (columnOpps.length || 1);

              return (
                <div key={column.status} className="text-center">
                  <p className="text-xs text-gray-500 mb-1">{column.title}</p>
                  <p className="text-2xl font-bold">{columnOpps.length}</p>
                  {avgScore > 0 && (
                    <p className="text-xs text-gray-500 mt-1">
                      Avg: {avgScore.toFixed(0)}/100
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DealPipeline;
