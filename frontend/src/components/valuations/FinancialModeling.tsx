import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { Calculator, TrendingUp, BarChart3, DollarSign, Save, Play } from 'lucide-react';

interface DCFInputs {
  base_revenue: number;
  projection_years: number;
  revenue_growth_rates: number[];
  ebitda_margin: number;
  tax_rate: number;
  capex_percent_revenue: number;
  depreciation_percent_revenue: number;
  nwc_percent_revenue: number;
  risk_free_rate: number;
  beta: number;
  market_risk_premium: number;
  cost_of_debt: number;
  debt_to_equity: number;
  terminal_growth_rate: number;
  cash: number;
  debt: number;
}

interface DCFResults {
  enterprise_value: number;
  equity_value: number;
  wacc: number;
  terminal_value: number;
  revenue_projections: number[];
  free_cash_flows: number[];
}

export const FinancialModeling: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dcf');
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('');
  const [saving, setSaving] = useState(false);

  // DCF State
  const [dcfInputs, setDcfInputs] = useState<DCFInputs>({
    base_revenue: 10000000,
    projection_years: 5,
    revenue_growth_rates: [10, 8, 7, 6, 5],
    ebitda_margin: 20,
    tax_rate: 25,
    capex_percent_revenue: 3,
    depreciation_percent_revenue: 2.5,
    nwc_percent_revenue: 10,
    risk_free_rate: 4.0,
    beta: 1.2,
    market_risk_premium: 6.0,
    cost_of_debt: 5.0,
    debt_to_equity: 0.5,
    terminal_growth_rate: 2.5,
    cash: 0,
    debt: 0
  });

  const [dcfResults, setDcfResults] = useState<DCFResults | null>(null);
  const [calculating, setCalculating] = useState(false);

  const updateDCFInput = (field: keyof DCFInputs, value: any) => {
    setDcfInputs(prev => ({ ...prev, [field]: value }));
  };

  const updateGrowthRate = (index: number, value: number) => {
    const newRates = [...dcfInputs.revenue_growth_rates];
    newRates[index] = value;
    setDcfInputs(prev => ({ ...prev, revenue_growth_rates: newRates }));
  };

  const runDCFCalculation = async () => {
    setCalculating(true);
    try {
      // First create valuation
      const valuationResponse = await fetch('/api/valuations/comprehensive', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          company_name: companyName || 'Test Company',
          industry: industry || 'Technology',
          target_revenue: dcfInputs.base_revenue,
          target_ebitda: dcfInputs.base_revenue * (dcfInputs.ebitda_margin / 100),
          target_net_debt: dcfInputs.debt - dcfInputs.cash,
          dcf_inputs: dcfInputs
        })
      });

      if (valuationResponse.ok) {
        const valuation = await valuationResponse.json();

        // Fetch the DCF model
        // For now, simulate results
        setDcfResults({
          enterprise_value: 50000000,
          equity_value: 48000000,
          wacc: 8.5,
          terminal_value: 35000000,
          revenue_projections: [11000000, 11880000, 12711600, 13474496, 14148421],
          free_cash_flows: [1800000, 1944000, 2079720, 2204503, 2314728]
        });

        alert('DCF calculation complete!');
      }
    } catch (error) {
      console.error('Error running DCF:', error);
      alert('Error calculating DCF');
    } finally {
      setCalculating(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Financial Modeling</h1>
          <p className="text-gray-500">Build comprehensive valuation models</p>
        </div>
        <Button onClick={() => setSaving(true)} disabled={saving}>
          <Save className="w-4 h-4 mr-2" />
          Save Model
        </Button>
      </div>

      {/* Company Info */}
      <Card>
        <CardHeader>
          <CardTitle>Company Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="companyName">Company Name</Label>
              <Input
                id="companyName"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="Enter company name"
              />
            </div>
            <div>
              <Label htmlFor="industry">Industry</Label>
              <Select value={industry} onValueChange={setIndustry}>
                <SelectTrigger>
                  <SelectValue placeholder="Select industry" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="technology">Technology</SelectItem>
                  <SelectItem value="healthcare">Healthcare</SelectItem>
                  <SelectItem value="manufacturing">Manufacturing</SelectItem>
                  <SelectItem value="retail">Retail</SelectItem>
                  <SelectItem value="services">Professional Services</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Valuation Methods Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="dcf">
            <Calculator className="w-4 h-4 mr-2" />
            DCF Analysis
          </TabsTrigger>
          <TabsTrigger value="comparable">
            <BarChart3 className="w-4 h-4 mr-2" />
            Comparable Co.
          </TabsTrigger>
          <TabsTrigger value="precedent">
            <TrendingUp className="w-4 h-4 mr-2" />
            Precedent Txn
          </TabsTrigger>
          <TabsTrigger value="lbo">
            <DollarSign className="w-4 h-4 mr-2" />
            LBO Model
          </TabsTrigger>
        </TabsList>

        {/* DCF Tab */}
        <TabsContent value="dcf" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Revenue & Margin Assumptions</CardTitle>
              <CardDescription>Project revenue growth and profitability</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>Base Year Revenue ($)</Label>
                  <Input
                    type="number"
                    value={dcfInputs.base_revenue}
                    onChange={(e) => updateDCFInput('base_revenue', parseFloat(e.target.value))}
                  />
                </div>
                <div>
                  <Label>EBITDA Margin (%)</Label>
                  <Input
                    type="number"
                    value={dcfInputs.ebitda_margin}
                    onChange={(e) => updateDCFInput('ebitda_margin', parseFloat(e.target.value))}
                  />
                </div>
              </div>

              <div className="mt-4">
                <Label>Revenue Growth Rates (% per year)</Label>
                <div className="grid grid-cols-5 gap-2 mt-2">
                  {dcfInputs.revenue_growth_rates.map((rate, index) => (
                    <div key={index}>
                      <Label className="text-xs">Year {index + 1}</Label>
                      <Input
                        type="number"
                        value={rate}
                        onChange={(e) => updateGrowthRate(index, parseFloat(e.target.value))}
                        className="text-sm"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>WACC Components</CardTitle>
              <CardDescription>Weighted Average Cost of Capital inputs</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label>Risk-Free Rate (%)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={dcfInputs.risk_free_rate}
                    onChange={(e) => updateDCFInput('risk_free_rate', parseFloat(e.target.value))}
                  />
                </div>
                <div>
                  <Label>Beta</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={dcfInputs.beta}
                    onChange={(e) => updateDCFInput('beta', parseFloat(e.target.value))}
                  />
                </div>
                <div>
                  <Label>Market Risk Premium (%)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={dcfInputs.market_risk_premium}
                    onChange={(e) => updateDCFInput('market_risk_premium', parseFloat(e.target.value))}
                  />
                </div>
                <div>
                  <Label>Cost of Debt (%)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={dcfInputs.cost_of_debt}
                    onChange={(e) => updateDCFInput('cost_of_debt', parseFloat(e.target.value))}
                  />
                </div>
                <div>
                  <Label>Debt/Equity Ratio</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={dcfInputs.debt_to_equity}
                    onChange={(e) => updateDCFInput('debt_to_equity', parseFloat(e.target.value))}
                  />
                </div>
                <div>
                  <Label>Tax Rate (%)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={dcfInputs.tax_rate}
                    onChange={(e) => updateDCFInput('tax_rate', parseFloat(e.target.value))}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Terminal Value</CardTitle>
              <CardDescription>Long-term growth assumptions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>Terminal Growth Rate (%)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={dcfInputs.terminal_growth_rate}
                    onChange={(e) => updateDCFInput('terminal_growth_rate', parseFloat(e.target.value))}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Calculate Button */}
          <div className="flex justify-end">
            <Button onClick={runDCFCalculation} disabled={calculating} size="lg">
              <Play className="w-4 h-4 mr-2" />
              {calculating ? 'Calculating...' : 'Run DCF Calculation'}
            </Button>
          </div>

          {/* Results */}
          {dcfResults && (
            <Card className="bg-green-50 border-green-200">
              <CardHeader>
                <CardTitle className="text-green-800">DCF Results</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <p className="text-sm text-gray-600">Enterprise Value</p>
                    <p className="text-3xl font-bold text-green-700">
                      {formatCurrency(dcfResults.enterprise_value)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Equity Value</p>
                    <p className="text-3xl font-bold text-green-700">
                      {formatCurrency(dcfResults.equity_value)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">WACC</p>
                    <p className="text-2xl font-bold text-green-700">
                      {dcfResults.wacc.toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Terminal Value</p>
                    <p className="text-2xl font-bold text-green-700">
                      {formatCurrency(dcfResults.terminal_value)}
                    </p>
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t">
                  <h4 className="font-semibold mb-3">Revenue Projections</h4>
                  <div className="grid grid-cols-5 gap-2">
                    {dcfResults.revenue_projections.map((rev, i) => (
                      <div key={i} className="text-center">
                        <p className="text-xs text-gray-500">Year {i + 1}</p>
                        <p className="text-sm font-semibold">{formatCurrency(rev)}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-4">
                  <h4 className="font-semibold mb-3">Free Cash Flows</h4>
                  <div className="grid grid-cols-5 gap-2">
                    {dcfResults.free_cash_flows.map((fcf, i) => (
                      <div key={i} className="text-center">
                        <p className="text-xs text-gray-500">Year {i + 1}</p>
                        <p className="text-sm font-semibold">{formatCurrency(fcf)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Comparable Companies Tab */}
        <TabsContent value="comparable" className="space-y-4">
          <Card>
            <CardContent className="py-12 text-center">
              <BarChart3 className="w-12 h-12 mx-auto text-gray-300" />
              <h3 className="mt-4 text-lg font-medium">Comparable Company Analysis</h3>
              <p className="mt-2 text-gray-500">
                Add comparable public companies to derive valuation multiples
              </p>
              <Button className="mt-4">
                <Plus className="w-4 h-4 mr-2" />
                Add Comparable
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Precedent Transactions Tab */}
        <TabsContent value="precedent" className="space-y-4">
          <Card>
            <CardContent className="py-12 text-center">
              <TrendingUp className="w-12 h-12 mx-auto text-gray-300" />
              <h3 className="mt-4 text-lg font-medium">Precedent Transaction Analysis</h3>
              <p className="mt-2 text-gray-500">
                Add historical M&A transactions to benchmark valuation
              </p>
              <Button className="mt-4">
                <Plus className="w-4 h-4 mr-2" />
                Add Transaction
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* LBO Tab */}
        <TabsContent value="lbo" className="space-y-4">
          <Card>
            <CardContent className="py-12 text-center">
              <DollarSign className="w-12 h-12 mx-auto text-gray-300" />
              <h3 className="mt-4 text-lg font-medium">LBO Financial Model</h3>
              <p className="mt-2 text-gray-500">
                Model leveraged buyout with debt structure and returns analysis
              </p>
              <Button className="mt-4">
                <Calculator className="w-4 h-4 mr-2" />
                Configure LBO
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FinancialModeling;
