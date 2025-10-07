import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Calculator,
  TrendingUp,
  DollarSign,
  FileText,
  Plus,
  Eye,
  Download,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react';

interface Valuation {
  id: string;
  company_name: string;
  industry: string;
  primary_method: 'dcf' | 'comparable_company' | 'precedent_transaction' | 'lbo';
  base_case_value: number;
  optimistic_value?: number;
  pessimistic_value?: number;
  ev_revenue_multiple?: number;
  ev_ebitda_multiple?: number;
  status: 'draft' | 'in_review' | 'approved' | 'final';
  valuation_date: string;
}

const methodLabels = {
  dcf: 'DCF Analysis',
  comparable_company: 'Comparable Company',
  precedent_transaction: 'Precedent Transaction',
  lbo: 'LBO Model'
};

const statusColors = {
  draft: 'bg-gray-100 text-gray-800',
  in_review: 'bg-blue-100 text-blue-800',
  approved: 'bg-green-100 text-green-800',
  final: 'bg-purple-100 text-purple-800'
};

export const ValuationDashboard: React.FC = () => {
  const [valuations, setValuations] = useState<Valuation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedValuation, setSelectedValuation] = useState<Valuation | null>(null);

  useEffect(() => {
    fetchValuations();
  }, []);

  const fetchValuations = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/valuations', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setValuations(data);
      }
    } catch (error) {
      console.error('Error fetching valuations:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(amount);
  };

  const formatMultiple = (multiple?: number) => {
    if (!multiple) return 'N/A';
    return `${multiple.toFixed(1)}x`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getValuationRange = (val: Valuation) => {
    if (val.pessimistic_value && val.optimistic_value) {
      return `${formatCurrency(val.pessimistic_value)} - ${formatCurrency(val.optimistic_value)}`;
    }
    return 'N/A';
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Valuation Models</h1>
          <p className="text-gray-500">Financial modeling and M&A valuation analysis</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => window.location.href = '/valuations/new'}>
            <Plus className="w-4 h-4 mr-2" />
            New Valuation
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Valuations</CardTitle>
            <Calculator className="w-4 h-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{valuations.length}</div>
            <p className="text-xs text-gray-500 mt-1">Active models</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Approved Models</CardTitle>
            <FileText className="w-4 h-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {valuations.filter(v => v.status === 'approved' || v.status === 'final').length}
            </div>
            <p className="text-xs text-gray-500 mt-1">Ready for use</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg Enterprise Value</CardTitle>
            <TrendingUp className="w-4 h-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(
                valuations.reduce((sum, v) => sum + (v.base_case_value || 0), 0) /
                (valuations.length || 1)
              )}
            </div>
            <p className="text-xs text-gray-500 mt-1">Base case average</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg EV/EBITDA</CardTitle>
            <BarChart3 className="w-4 h-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatMultiple(
                valuations.reduce((sum, v) => sum + (v.ev_ebitda_multiple || 0), 0) /
                (valuations.filter(v => v.ev_ebitda_multiple).length || 1)
              )}
            </div>
            <p className="text-xs text-gray-500 mt-1">Portfolio average</p>
          </CardContent>
        </Card>
      </div>

      {/* Valuations Grid */}
      {loading ? (
        <div className="text-center py-12">
          <Calculator className="w-12 h-12 mx-auto text-gray-300 animate-pulse" />
          <p className="mt-4 text-gray-500">Loading valuations...</p>
        </div>
      ) : valuations.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Calculator className="w-12 h-12 mx-auto text-gray-300" />
            <h3 className="mt-4 text-lg font-medium">No valuations yet</h3>
            <p className="mt-2 text-gray-500">Create your first valuation model to get started</p>
            <Button onClick={() => window.location.href = '/valuations/new'} className="mt-4">
              <Plus className="w-4 h-4 mr-2" />
              Create Valuation
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {valuations.map((val) => (
            <Card
              key={val.id}
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => setSelectedValuation(val)}
            >
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{val.company_name}</CardTitle>
                    <CardDescription className="mt-1">
                      {val.industry} • {formatDate(val.valuation_date)}
                    </CardDescription>
                  </div>
                  <Badge className={statusColors[val.status]}>
                    {val.status.replace('_', ' ')}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Valuation Method */}
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {methodLabels[val.primary_method]}
                    </Badge>
                  </div>

                  {/* Enterprise Value */}
                  <div>
                    <p className="text-sm text-gray-500">Base Case Enterprise Value</p>
                    <p className="text-2xl font-bold text-green-600">
                      {formatCurrency(val.base_case_value)}
                    </p>
                  </div>

                  {/* Valuation Range */}
                  {val.pessimistic_value && val.optimistic_value && (
                    <div>
                      <p className="text-sm text-gray-500">Valuation Range</p>
                      <p className="text-sm font-semibold">
                        {getValuationRange(val)}
                      </p>
                    </div>
                  )}

                  {/* Multiples */}
                  <div className="grid grid-cols-2 gap-4 pt-2 border-t">
                    <div>
                      <p className="text-xs text-gray-500">EV/Revenue</p>
                      <p className="text-lg font-semibold">
                        {formatMultiple(val.ev_revenue_multiple)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">EV/EBITDA</p>
                      <p className="text-lg font-semibold">
                        {formatMultiple(val.ev_ebitda_multiple)}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        window.location.href = `/valuations/${val.id}`;
                      }}
                    >
                      <Eye className="w-3 h-3 mr-1" />
                      View
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        // Download report
                      }}
                    >
                      <Download className="w-3 h-3 mr-1" />
                      Report
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Method Distribution Chart Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Valuation Methods Used</CardTitle>
          <CardDescription>Distribution of valuation methodologies</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <PieChart className="w-12 h-12 mx-auto text-gray-300" />
              <p className="mt-4 text-gray-500">Chart visualization would go here</p>
              <p className="text-sm text-gray-400">DCF, Comparable, Precedent, LBO distribution</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Valuation Trends Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Valuation Trends</CardTitle>
          <CardDescription>Enterprise value trends over time</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <LineChart className="w-12 h-12 mx-auto text-gray-300" />
              <p className="mt-4 text-gray-500">Time series chart would go here</p>
              <p className="text-sm text-gray-400">Historical valuations and multiples</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ValuationDashboard;
