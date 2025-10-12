import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  ArrowLeft,
  Edit,
  Share2,
  MoreHorizontal,
  Calendar,
  DollarSign,
  Users,
  FileText,
} from 'lucide-react';

const DealDetail = () => {
  const { dealId } = useParams();

  // Mock deal data
  const deal = {
    id: dealId,
    name: 'TechCo Acquisition',
    targetCompany: 'TechCo Ltd',
    value: '£45.2M',
    stage: 'Due Diligence',
    priority: 'critical',
    progress: 75,
    lead: 'Sarah Chen',
    team: ['John Smith', 'Michael Brown', 'Lisa Johnson'],
    created: '2025-09-15',
    expectedClose: '2025-12-30',
    description:
      'Strategic acquisition of leading technology company to expand our digital capabilities in the financial services sector.',
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Pipeline
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{deal.name}</h1>
            <p className="text-gray-600">{deal.targetCompany}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <Badge variant="outline" className="text-red-600 border-red-200">
            {deal.priority}
          </Badge>
          <Badge variant="secondary">{deal.stage}</Badge>
          <Button variant="outline" size="sm">
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
          <Button variant="ghost" size="sm">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Deal Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              <span className="text-sm font-medium">Deal Value</span>
            </div>
            <div className="text-2xl font-bold mt-1">{deal.value}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Calendar className="h-5 w-5 text-blue-600" />
              <span className="text-sm font-medium">Expected Close</span>
            </div>
            <div className="text-lg font-semibold mt-1">{deal.expectedClose}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-purple-600" />
              <span className="text-sm font-medium">Team Size</span>
            </div>
            <div className="text-2xl font-bold mt-1">{deal.team.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <FileText className="h-5 w-5 text-orange-600" />
              <span className="text-sm font-medium">Progress</span>
            </div>
            <div className="text-2xl font-bold mt-1">{deal.progress}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Deal Information */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Deal Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">{deal.description}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Activity Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">Activity timeline coming soon</div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Deal Team</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-blue-600">SC</span>
                  </div>
                  <div>
                    <p className="font-medium">{deal.lead}</p>
                    <p className="text-sm text-gray-600">Deal Lead</p>
                  </div>
                </div>
                {deal.team.map((member, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-600">
                        {member
                          .split(' ')
                          .map((n) => n[0])
                          .join('')}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium">{member}</p>
                      <p className="text-sm text-gray-600">Team Member</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Documents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">No documents uploaded yet</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DealDetail;
