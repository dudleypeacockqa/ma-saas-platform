import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { UserPlus, Search, Filter, Mail, Phone, MoreHorizontal } from 'lucide-react';

const TeamMembers = () => {
  const members = [
    {
      id: 1,
      name: 'Sarah Chen',
      email: 'sarah.chen@company.com',
      phone: '+44 20 1234 5678',
      role: 'Senior Partner',
      department: 'M&A',
      location: 'London, UK',
      joined: '2020-01-15',
      status: 'active',
    },
    {
      id: 2,
      name: 'John Mitchell',
      email: 'john.mitchell@company.com',
      phone: '+44 20 1234 5679',
      role: 'VP of M&A',
      department: 'M&A',
      location: 'Manchester, UK',
      joined: '2021-03-20',
      status: 'active',
    },
    {
      id: 3,
      name: 'Michael Brown',
      email: 'michael.brown@company.com',
      phone: '+44 20 1234 5680',
      role: 'Senior Advisor',
      department: 'Advisory',
      location: 'Edinburgh, UK',
      joined: '2019-08-10',
      status: 'active',
    },
    {
      id: 4,
      name: 'Lisa Johnson',
      email: 'lisa.johnson@company.com',
      phone: '+44 20 1234 5681',
      role: 'Associate',
      department: 'M&A',
      location: 'Birmingham, UK',
      joined: '2023-01-05',
      status: 'pending',
    },
  ];

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Team Members</h1>
          <p className="text-gray-600">Manage team member details and permissions</p>
        </div>

        <Button>
          <UserPlus className="h-4 w-4 mr-2" />
          Invite Member
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center space-x-4 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="Search team members..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <Button variant="outline" size="sm">
          <Filter className="h-4 w-4 mr-2" />
          Filter
        </Button>
      </div>

      {/* Members List */}
      <Card>
        <CardHeader>
          <CardTitle>All Members ({members.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {members.map((member) => (
              <div
                key={member.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
              >
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-blue-600">
                      {member.name
                        .split(' ')
                        .map((n) => n[0])
                        .join('')}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{member.name}</h3>
                    <p className="text-sm text-gray-600">
                      {member.role} • {member.department}
                    </p>
                    <p className="text-sm text-gray-500">{member.location}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-6">
                  <div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Mail className="h-4 w-4" />
                      <span>{member.email}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600 mt-1">
                      <Phone className="h-4 w-4" />
                      <span>{member.phone}</span>
                    </div>
                  </div>

                  <div className="text-center">
                    <p className="text-sm text-gray-600">Joined</p>
                    <p className="text-sm font-medium text-gray-900">{member.joined}</p>
                  </div>

                  <Badge
                    variant={member.status === 'active' ? 'default' : 'secondary'}
                    className="capitalize"
                  >
                    {member.status}
                  </Badge>

                  <Button variant="ghost" size="sm">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TeamMembers;
