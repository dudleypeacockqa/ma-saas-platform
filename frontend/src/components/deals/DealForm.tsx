import React, { useState, useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { format } from 'date-fns'
import { Calendar as CalendarIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Calendar } from '@/components/ui/calendar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import {
  Building2,
  DollarSign,
  Users,
  FileText,
  TrendingUp,
  Calendar as CalendarIcon2,
  AlertCircle,
  Plus,
  X,
  Loader2,
  Save,
  ChevronRight
} from 'lucide-react'

// Form validation schema
const dealFormSchema = z.object({
  // Basic Information
  title: z.string().min(1, 'Deal title is required').max(255),
  codeNam: z.string().optional(),
  dealType: z.string().min(1, 'Deal type is required'),
  stage: z.string().min(1, 'Deal stage is required'),
  priority: z.string().min(1, 'Priority is required'),

  // Target Company
  targetCompanyName: z.string().min(1, 'Target company name is required'),
  targetCompanyWebsite: z.string().url().optional().or(z.literal('')),
  targetCompanyDescription: z.string().optional(),
  targetIndustry: z.string().optional(),
  targetCountry: z.string().optional(),
  targetEmployees: z.number().optional(),

  // Financial Information
  dealValue: z.number().min(0, 'Deal value must be positive'),
  dealCurrency: z.string().min(1, 'Currency is required'),
  enterpriseValue: z.number().optional(),
  equityValue: z.number().optional(),
  debtAssumed: z.number().optional(),
  revenueMultiple: z.number().optional(),
  ebitdaMultiple: z.number().optional(),
  targetRevenue: z.number().optional(),
  targetEbitda: z.number().optional(),

  // Deal Structure
  cashConsideration: z.number().optional(),
  stockConsideration: z.number().optional(),
  earnoutConsideration: z.number().optional(),
  ownershipPercentage: z.number().min(0).max(100).optional(),

  // Important Dates
  initialContactDate: z.date().optional(),
  expectedCloseDate: z.date().optional(),

  // Deal Team
  dealLeadId: z.string().optional(),

  // Status and Tracking
  probabilityOfClose: z.number().min(0).max(100),
  riskLevel: z.string().optional(),

  // Notes
  executiveSummary: z.string().optional(),
  investmentThesis: z.string().optional(),
  keyRisks: z.array(z.string()).optional(),
  keyOpportunities: z.array(z.string()).optional(),
  nextSteps: z.string().optional(),

  // Tags
  tags: z.array(z.string()).optional(),
})

type DealFormData = z.infer<typeof dealFormSchema>

interface DealFormProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: DealFormData) => Promise<void>
  initialData?: Partial<DealFormData>
  mode: 'create' | 'edit'
}

const DEAL_TYPES = [
  { value: 'acquisition', label: 'Acquisition' },
  { value: 'merger', label: 'Merger' },
  { value: 'divestiture', label: 'Divestiture' },
  { value: 'joint_venture', label: 'Joint Venture' },
  { value: 'management_buyout', label: 'Management Buyout' },
  { value: 'leveraged_buyout', label: 'Leveraged Buyout' },
  { value: 'asset_purchase', label: 'Asset Purchase' },
  { value: 'stock_purchase', label: 'Stock Purchase' },
]

const DEAL_STAGES = [
  { value: 'sourcing', label: 'Sourcing' },
  { value: 'initial_review', label: 'Initial Review' },
  { value: 'nda_execution', label: 'NDA Execution' },
  { value: 'preliminary_analysis', label: 'Preliminary Analysis' },
  { value: 'valuation', label: 'Valuation' },
  { value: 'due_diligence', label: 'Due Diligence' },
  { value: 'negotiation', label: 'Negotiation' },
  { value: 'loi_drafting', label: 'LOI Drafting' },
  { value: 'documentation', label: 'Documentation' },
  { value: 'closing', label: 'Closing' },
]

const PRIORITIES = [
  { value: 'critical', label: 'Critical', color: 'text-red-600' },
  { value: 'high', label: 'High', color: 'text-orange-600' },
  { value: 'medium', label: 'Medium', color: 'text-yellow-600' },
  { value: 'low', label: 'Low', color: 'text-gray-600' },
]

const RISK_LEVELS = [
  { value: 'low', label: 'Low Risk' },
  { value: 'medium', label: 'Medium Risk' },
  { value: 'high', label: 'High Risk' },
  { value: 'critical', label: 'Critical Risk' },
]

const CURRENCIES = [
  { value: 'USD', label: 'USD - US Dollar' },
  { value: 'EUR', label: 'EUR - Euro' },
  { value: 'GBP', label: 'GBP - British Pound' },
  { value: 'JPY', label: 'JPY - Japanese Yen' },
  { value: 'CHF', label: 'CHF - Swiss Franc' },
  { value: 'CAD', label: 'CAD - Canadian Dollar' },
  { value: 'AUD', label: 'AUD - Australian Dollar' },
]

const INDUSTRIES = [
  { value: 'technology', label: 'Technology' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'finance', label: 'Financial Services' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'retail', label: 'Retail' },
  { value: 'energy', label: 'Energy' },
  { value: 'real_estate', label: 'Real Estate' },
  { value: 'consumer_goods', label: 'Consumer Goods' },
  { value: 'telecom', label: 'Telecommunications' },
  { value: 'media', label: 'Media & Entertainment' },
]

export const DealForm: React.FC<DealFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialData,
  mode,
}) => {
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('basic')
  const [newRisk, setNewRisk] = useState('')
  const [newOpportunity, setNewOpportunity] = useState('')
  const [newTag, setNewTag] = useState('')

  const form = useForm<DealFormData>({
    resolver: zodResolver(dealFormSchema),
    defaultValues: {
      dealCurrency: 'USD',
      dealType: 'acquisition',
      stage: 'sourcing',
      priority: 'medium',
      probabilityOfClose: 50,
      keyRisks: [],
      keyOpportunities: [],
      tags: [],
      ...initialData,
    },
  })

  const handleFormSubmit = async (data: DealFormData) => {
    setLoading(true)
    try {
      await onSubmit(data)
      form.reset()
      onClose()
    } catch (error) {
      console.error('Error submitting deal:', error)
    } finally {
      setLoading(false)
    }
  }

  const addRisk = () => {
    if (newRisk.trim()) {
      const currentRisks = form.getValues('keyRisks') || []
      form.setValue('keyRisks', [...currentRisks, newRisk.trim()])
      setNewRisk('')
    }
  }

  const removeRisk = (index: number) => {
    const currentRisks = form.getValues('keyRisks') || []
    form.setValue('keyRisks', currentRisks.filter((_, i) => i !== index))
  }

  const addOpportunity = () => {
    if (newOpportunity.trim()) {
      const currentOps = form.getValues('keyOpportunities') || []
      form.setValue('keyOpportunities', [...currentOps, newOpportunity.trim()])
      setNewOpportunity('')
    }
  }

  const removeOpportunity = (index: number) => {
    const currentOps = form.getValues('keyOpportunities') || []
    form.setValue('keyOpportunities', currentOps.filter((_, i) => i !== index))
  }

  const addTag = () => {
    if (newTag.trim()) {
      const currentTags = form.getValues('tags') || []
      form.setValue('tags', [...currentTags, newTag.trim()])
      setNewTag('')
    }
  }

  const removeTag = (index: number) => {
    const currentTags = form.getValues('tags') || []
    form.setValue('tags', currentTags.filter((_, i) => i !== index))
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {mode === 'create' ? 'Create New Deal' : 'Edit Deal'}
          </DialogTitle>
          <DialogDescription>
            {mode === 'create'
              ? 'Enter the details for the new M&A transaction.'
              : 'Update the deal information and save changes.'}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleFormSubmit)} className="space-y-6">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="basic">Basic</TabsTrigger>
                <TabsTrigger value="target">Target</TabsTrigger>
                <TabsTrigger value="financial">Financial</TabsTrigger>
                <TabsTrigger value="structure">Structure</TabsTrigger>
                <TabsTrigger value="notes">Notes</TabsTrigger>
              </TabsList>

              <TabsContent value="basic" className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="title"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Deal Title *</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter deal title" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="codeNam"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Code Name</FormLabel>
                        <FormControl>
                          <Input placeholder="Project Alpha" {...field} />
                        </FormControl>
                        <FormDescription>Internal code name for confidentiality</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <FormField
                    control={form.control}
                    name="dealType"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Deal Type *</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select type" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {DEAL_TYPES.map(type => (
                              <SelectItem key={type.value} value={type.value}>
                                {type.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="stage"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Stage *</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select stage" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {DEAL_STAGES.map(stage => (
                              <SelectItem key={stage.value} value={stage.value}>
                                {stage.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="priority"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Priority *</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select priority" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {PRIORITIES.map(priority => (
                              <SelectItem key={priority.value} value={priority.value}>
                                <span className={priority.color}>{priority.label}</span>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="probabilityOfClose"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Probability of Close: {field.value}%</FormLabel>
                        <FormControl>
                          <Slider
                            min={0}
                            max={100}
                            step={5}
                            value={[field.value]}
                            onValueChange={([value]) => field.onChange(value)}
                            className="mt-2"
                          />
                        </FormControl>
                        <FormDescription>Estimated likelihood of successful closing</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="riskLevel"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Risk Level</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select risk level" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {RISK_LEVELS.map(risk => (
                              <SelectItem key={risk.value} value={risk.value}>
                                {risk.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Tags</Label>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add tag"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault()
                          addTag()
                        }
                      }}
                    />
                    <Button type="button" onClick={addTag} size="sm">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {form.watch('tags')?.map((tag, index) => (
                      <Badge key={index} variant="secondary">
                        {tag}
                        <button
                          type="button"
                          onClick={() => removeTag(index)}
                          className="ml-2 hover:text-red-500"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="target" className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="targetCompanyName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Target Company Name *</FormLabel>
                        <FormControl>
                          <Input placeholder="Company name" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="targetCompanyWebsite"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Website</FormLabel>
                        <FormControl>
                          <Input placeholder="https://example.com" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="targetCompanyDescription"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Company Description</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Brief description of the target company..."
                          className="resize-none"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="grid grid-cols-3 gap-4">
                  <FormField
                    control={form.control}
                    name="targetIndustry"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Industry</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select industry" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {INDUSTRIES.map(industry => (
                              <SelectItem key={industry.value} value={industry.value}>
                                {industry.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="targetCountry"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Country</FormLabel>
                        <FormControl>
                          <Input placeholder="US" maxLength={2} {...field} />
                        </FormControl>
                        <FormDescription>ISO country code</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="targetEmployees"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Employees</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="500"
                            {...field}
                            onChange={(e) => field.onChange(parseInt(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </TabsContent>

              <TabsContent value="financial" className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="dealValue"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Deal Value *</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="0"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="dealCurrency"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Currency *</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select currency" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {CURRENCIES.map(currency => (
                              <SelectItem key={currency.value} value={currency.value}>
                                {currency.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <FormField
                    control={form.control}
                    name="enterpriseValue"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Enterprise Value</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="0"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="equityValue"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Equity Value</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="0"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="debtAssumed"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Debt Assumed</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="0"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <Separator />

                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="targetRevenue"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Target Annual Revenue</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="0"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="targetEbitda"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Target EBITDA</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="0"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="revenueMultiple"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Revenue Multiple</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            step="0.1"
                            placeholder="0.0x"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="ebitdaMultiple"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>EBITDA Multiple</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            step="0.1"
                            placeholder="0.0x"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </TabsContent>

              <TabsContent value="structure" className="space-y-4 mt-4">
                <div className="space-y-4">
                  <h3 className="text-sm font-medium">Deal Consideration</h3>

                  <div className="grid grid-cols-3 gap-4">
                    <FormField
                      control={form.control}
                      name="cashConsideration"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Cash Component</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              placeholder="0"
                              {...field}
                              onChange={(e) => field.onChange(parseFloat(e.target.value))}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="stockConsideration"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Stock Component</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              placeholder="0"
                              {...field}
                              onChange={(e) => field.onChange(parseFloat(e.target.value))}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="earnoutConsideration"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Earnout Component</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              placeholder="0"
                              {...field}
                              onChange={(e) => field.onChange(parseFloat(e.target.value))}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <FormField
                    control={form.control}
                    name="ownershipPercentage"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Ownership Percentage: {field.value}%</FormLabel>
                        <FormControl>
                          <Slider
                            min={0}
                            max={100}
                            step={1}
                            value={[field.value || 0]}
                            onValueChange={([value]) => field.onChange(value)}
                            className="mt-2"
                          />
                        </FormControl>
                        <FormDescription>Percentage of ownership to be acquired</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <Separator />

                <div className="space-y-4">
                  <h3 className="text-sm font-medium">Important Dates</h3>

                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="initialContactDate"
                      render={({ field }) => (
                        <FormItem className="flex flex-col">
                          <FormLabel>Initial Contact Date</FormLabel>
                          <Popover>
                            <PopoverTrigger asChild>
                              <FormControl>
                                <Button
                                  variant="outline"
                                  className={cn(
                                    "w-full pl-3 text-left font-normal",
                                    !field.value && "text-muted-foreground"
                                  )}
                                >
                                  {field.value ? (
                                    format(field.value, "PPP")
                                  ) : (
                                    <span>Pick a date</span>
                                  )}
                                  <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                                </Button>
                              </FormControl>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="start">
                              <Calendar
                                mode="single"
                                selected={field.value}
                                onSelect={field.onChange}
                                disabled={(date) =>
                                  date > new Date() || date < new Date("1900-01-01")
                                }
                                initialFocus
                              />
                            </PopoverContent>
                          </Popover>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="expectedCloseDate"
                      render={({ field }) => (
                        <FormItem className="flex flex-col">
                          <FormLabel>Expected Close Date</FormLabel>
                          <Popover>
                            <PopoverTrigger asChild>
                              <FormControl>
                                <Button
                                  variant="outline"
                                  className={cn(
                                    "w-full pl-3 text-left font-normal",
                                    !field.value && "text-muted-foreground"
                                  )}
                                >
                                  {field.value ? (
                                    format(field.value, "PPP")
                                  ) : (
                                    <span>Pick a date</span>
                                  )}
                                  <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                                </Button>
                              </FormControl>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="start">
                              <Calendar
                                mode="single"
                                selected={field.value}
                                onSelect={field.onChange}
                                disabled={(date) =>
                                  date < new Date()
                                }
                                initialFocus
                              />
                            </PopoverContent>
                          </Popover>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="notes" className="space-y-4 mt-4">
                <FormField
                  control={form.control}
                  name="executiveSummary"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Executive Summary</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Brief overview of the deal..."
                          className="resize-none h-24"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="investmentThesis"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Investment Thesis</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Strategic rationale for the transaction..."
                          className="resize-none h-24"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="space-y-2">
                  <Label>Key Risks</Label>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add risk"
                      value={newRisk}
                      onChange={(e) => setNewRisk(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault()
                          addRisk()
                        }
                      }}
                    />
                    <Button type="button" onClick={addRisk} size="sm">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="space-y-2 mt-2">
                    {form.watch('keyRisks')?.map((risk, index) => (
                      <div key={index} className="flex items-center gap-2 p-2 bg-red-50 rounded">
                        <AlertCircle className="h-4 w-4 text-red-500" />
                        <span className="flex-1 text-sm">{risk}</span>
                        <button
                          type="button"
                          onClick={() => removeRisk(index)}
                          className="hover:text-red-500"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Key Opportunities</Label>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add opportunity"
                      value={newOpportunity}
                      onChange={(e) => setNewOpportunity(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault()
                          addOpportunity()
                        }
                      }}
                    />
                    <Button type="button" onClick={addOpportunity} size="sm">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="space-y-2 mt-2">
                    {form.watch('keyOpportunities')?.map((opp, index) => (
                      <div key={index} className="flex items-center gap-2 p-2 bg-green-50 rounded">
                        <TrendingUp className="h-4 w-4 text-green-500" />
                        <span className="flex-1 text-sm">{opp}</span>
                        <button
                          type="button"
                          onClick={() => removeOpportunity(index)}
                          className="hover:text-red-500"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                <FormField
                  control={form.control}
                  name="nextSteps"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Next Steps</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Immediate action items..."
                          className="resize-none"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </TabsContent>
            </Tabs>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    {mode === 'create' ? 'Create Deal' : 'Save Changes'}
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default DealForm