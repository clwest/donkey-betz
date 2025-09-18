import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select-proper';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  User, Brain, MessageSquare, Target, Settings, BookOpen,
  Calendar, Clock, Coffee, Heart, Plane, AlertCircle, Lock
} from 'lucide-react';
import api from '@/services/api';

interface EnhancedProfileData {
  primary_role: string;
  secondary_roles: string[];
  long_term_goals: string[];
  current_projects: any[];
  quarterly_objectives: any;
  communication_style: string;
  decision_framework: string;
  time_zone: string;
  learning_style: string;
  core_competencies: Record<string, number>;
  profile_completeness: number;
  interaction_count: number;
  should_update: boolean;
}

interface Memory {
  id: string;
  type: string;
  content: string;
  importance: number;
  created_at: string;
  accessed_count: number;
}

export default function EnhancedProfile() {
  const [profile, setProfile] = useState<EnhancedProfileData | null>(null);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editMode, setEditMode] = useState<Record<string, boolean>>({});

  useEffect(() => {
    fetchProfile();
    fetchMemories();
    fetchSuggestions();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/api/profile/enhanced/');
      setProfile(response.data.profile);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMemories = async () => {
    try {
      const response = await api.get('/api/profile/memories/');
      setMemories(response.data.memories);
    } catch (error) {
      console.error('Failed to fetch memories:', error);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const response = await api.get('/api/profile/suggestions/');
      setSuggestions(response.data.suggestions);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    }
  };

  const updateProfile = async (category: string, fields: any) => {
    setSaving(true);
    try {
      await api.post('/api/profile/enhanced/update/', {
        category,
        fields
      });
      await fetchProfile();
      setEditMode({ ...editMode, [category]: false });
    } catch (error) {
      console.error('Failed to update profile:', error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  if (!profile) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Failed to load profile. Please try refreshing the page.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-primary to-primary/60 rounded-full flex items-center justify-center">
                  <User className="w-8 h-8 text-white" />
                </div>
                <div className="absolute -bottom-1 -right-1">
                  <Progress value={profile.profile_completeness} className="w-20 h-2" />
                </div>
              </div>
              <div>
                <CardTitle className="text-2xl">Enhanced Profile</CardTitle>
                <p className="text-sm text-muted-foreground">
                  {profile.profile_completeness.toFixed(0)}% Complete •
                  {profile.interaction_count} Interactions
                </p>
              </div>
            </div>
            {profile.should_update && (
              <Badge variant="outline" className="bg-yellow-50">
                Profile update recommended
              </Badge>
            )}
          </div>
        </CardHeader>
      </Card>

      {/* Profile Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-6 w-full">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="roles">Roles & Goals</TabsTrigger>
          <TabsTrigger value="communication">Communication</TabsTrigger>
          <TabsTrigger value="personal">Personal</TabsTrigger>
          <TabsTrigger value="skills">Skills</TabsTrigger>
          <TabsTrigger value="memories">Memories</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Primary Role
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xl font-medium">
                  {profile.primary_role || 'Not set'}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Communication Style
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xl font-medium capitalize">
                  {profile.communication_style}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Brain className="w-4 h-4" />
                  Decision Framework
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xl font-medium capitalize">
                  {profile.decision_framework.replace('_', ' ')}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <BookOpen className="w-4 h-4" />
                  Learning Style
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xl font-medium capitalize">
                  {profile.learning_style}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Improvement Suggestions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {suggestions.map((suggestion, idx) => (
                    <Alert key={idx}>
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>
                        {suggestion.message}
                        <Badge className="ml-2" variant={
                          suggestion.priority === 'high' ? 'destructive' :
                          suggestion.priority === 'medium' ? 'default' : 'secondary'
                        }>
                          {suggestion.priority}
                        </Badge>
                      </AlertDescription>
                    </Alert>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Roles & Goals Tab */}
        <TabsContent value="roles" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Roles & Goals</CardTitle>
                <Button
                  variant={editMode.roles_goals ? "default" : "outline"}
                  size="sm"
                  onClick={() => setEditMode({ ...editMode, roles_goals: !editMode.roles_goals })}
                >
                  {editMode.roles_goals ? 'Cancel' : 'Edit'}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {editMode.roles_goals ? (
                <div className="space-y-4">
                  <div>
                    <Label>Primary Role</Label>
                    <Input
                      value={profile.primary_role}
                      onChange={(e) => setProfile({ ...profile, primary_role: e.target.value })}
                      placeholder="e.g., Software Engineer, Product Manager"
                    />
                  </div>
                  <div>
                    <Label>Long-term Goals</Label>
                    <Textarea
                      value={profile.long_term_goals.join('\n')}
                      onChange={(e) => setProfile({
                        ...profile,
                        long_term_goals: e.target.value.split('\n').filter(Boolean)
                      })}
                      placeholder="Enter each goal on a new line"
                      rows={4}
                    />
                  </div>
                  <Button
                    onClick={() => updateProfile('roles_goals', {
                      primary_role: profile.primary_role,
                      long_term_goals: profile.long_term_goals
                    })}
                    disabled={saving}
                  >
                    {saving ? 'Saving...' : 'Save Changes'}
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Primary Role</p>
                    <p className="text-lg">{profile.primary_role || 'Not set'}</p>
                  </div>
                  {profile.long_term_goals.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Long-term Goals</p>
                      <ul className="list-disc list-inside space-y-1 mt-2">
                        {profile.long_term_goals.map((goal, idx) => (
                          <li key={idx}>{goal}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Communication Tab */}
        <TabsContent value="communication" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Communication Preferences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Communication Style</Label>
                  <Select
                    value={profile.communication_style}
                    onValueChange={(value) => updateProfile('communication', {
                      communication_style: value
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="concise">Concise</SelectItem>
                      <SelectItem value="detailed">Detailed</SelectItem>
                      <SelectItem value="balanced">Balanced</SelectItem>
                      <SelectItem value="visual">Visual</SelectItem>
                      <SelectItem value="narrative">Narrative</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Decision Framework</Label>
                  <Select
                    value={profile.decision_framework}
                    onValueChange={(value) => updateProfile('communication', {
                      decision_framework: value
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="data_driven">Data-Driven</SelectItem>
                      <SelectItem value="intuitive">Intuitive</SelectItem>
                      <SelectItem value="collaborative">Collaborative</SelectItem>
                      <SelectItem value="analytical">Analytical</SelectItem>
                      <SelectItem value="rapid">Rapid</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Memories Tab */}
        <TabsContent value="memories" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI Memory Context</CardTitle>
              <p className="text-sm text-muted-foreground">
                What the AI has learned about you
              </p>
            </CardHeader>
            <CardContent>
              {memories.length > 0 ? (
                <div className="space-y-3">
                  {memories.map((memory) => (
                    <div key={memory.id} className="p-3 border rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="outline">{memory.type}</Badge>
                            <span className="text-xs text-muted-foreground">
                              Importance: {memory.importance}/10
                            </span>
                          </div>
                          <p className="text-sm">{memory.content}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                        <span>Accessed {memory.accessed_count} times</span>
                        <span>
                          {new Date(memory.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No memories yet. Start chatting with the AI Assistant to build your memory context.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}