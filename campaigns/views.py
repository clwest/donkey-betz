"""
Views for campaigns app.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import uuid
from datetime import datetime

# In-memory storage for campaigns (will reset when server restarts)
CAMPAIGNS_STORAGE = {}

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def campaigns_list(request):
    """
    Get list of campaigns or create a new one.
    """
    if request.method == 'GET':
        # Return all campaigns from storage
        campaigns = list(CAMPAIGNS_STORAGE.values())
        return Response({'campaigns': campaigns})
    
    elif request.method == 'POST':
        # Create a new campaign
        data = request.data
        campaign_id = str(uuid.uuid4())
        campaign = {
            'id': campaign_id,
            'title': data.get('title', 'New Campaign'),
            'description': data.get('description', ''),
            'campaign_type': data.get('campaign_type', 'multi'),
            'target_audience': data.get('target_audience', ''),
            'status': 'draft',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'content': []
        }
        # Store in memory
        CAMPAIGNS_STORAGE[campaign_id] = campaign
        return Response(campaign, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def campaign_templates(request):
    """
    Get campaign templates.
    """
    return Response({
        'templates': [
            {
                'id': 1,
                'name': 'Email Campaign',
                'description': 'Template for email marketing campaigns',
                'type': 'email',
                'icon': 'EnvelopeIcon'
            },
            {
                'id': 2,
                'name': 'Social Media Campaign',
                'description': 'Template for social media campaigns',
                'type': 'social',
                'icon': 'MegaphoneIcon'
            },
            {
                'id': 3,
                'name': 'Content Marketing',
                'description': 'Template for content marketing campaigns',
                'type': 'content',
                'icon': 'DocumentTextIcon'
            }
        ]
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def create_from_template(request):
    """
    Create a campaign from a template.
    """
    data = request.data
    template_name = data.get('template_name', 'Custom')
    customizations = data.get('customizations', {})
    
    # Create campaign from template
    campaign_id = str(uuid.uuid4())
    campaign = {
        'id': campaign_id,
        'title': customizations.get('name', f'New {template_name}'),
        'description': f'Campaign created from {template_name} template',
        'campaign_type': 'multi',
        'target_audience': customizations.get('target_audience', {}).get('description', ''),
        'budget': customizations.get('budget', 0),
        'status': 'draft',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'template_used': template_name,
        'content': []
    }
    
    # Store in memory
    CAMPAIGNS_STORAGE[campaign_id] = campaign
    
    return Response(campaign, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def campaign_detail(request, campaign_id):
    """
    Get, update, or delete a specific campaign.
    """
    if request.method == 'GET':
        # Get campaign from storage
        campaign = CAMPAIGNS_STORAGE.get(campaign_id)
        if campaign:
            return Response({'campaign': campaign})
        else:
            # Return a default campaign if not found
            campaign = {
                'id': campaign_id,
                'title': 'Campaign Details',
                'description': 'This is a detailed view of the campaign',
                'campaign_type': 'multi',
                'target_audience': 'General audience',
                'status': 'draft',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'content': []
            }
            # Store it for future use
            CAMPAIGNS_STORAGE[campaign_id] = campaign
            return Response({'campaign': campaign})
    
    elif request.method == 'PUT':
        # Update campaign
        data = request.data
        existing = CAMPAIGNS_STORAGE.get(campaign_id, {})
        campaign = {
            'id': campaign_id,
            'title': data.get('title', existing.get('title', 'Updated Campaign')),
            'description': data.get('description', existing.get('description', '')),
            'campaign_type': data.get('campaign_type', existing.get('campaign_type', 'multi')),
            'target_audience': data.get('target_audience', existing.get('target_audience', '')),
            'status': data.get('status', existing.get('status', 'draft')),
            'created_at': existing.get('created_at', datetime.now().isoformat()),
            'updated_at': datetime.now().isoformat(),
            'content': existing.get('content', [])
        }
        # Update in storage
        CAMPAIGNS_STORAGE[campaign_id] = campaign
        return Response(campaign)
    
    elif request.method == 'DELETE':
        # Delete campaign from storage
        if campaign_id in CAMPAIGNS_STORAGE:
            del CAMPAIGNS_STORAGE[campaign_id]
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_simple_content(request, campaign_id):
    """
    Generate simple content for a campaign.
    """
    data = request.data
    content_type = data.get('content_type', 'email')
    prompt = data.get('prompt', '')
    
    # Generate mock content based on type
    content_templates = {
        'email': {
            'subject': 'Exciting News About Our Latest Offer!',
            'content': f'Dear Valued Customer,\n\nWe have something special for you! {prompt}\n\nBest regards,\nYour Team',
            'preview': 'Check out our latest updates and exclusive offers...'
        },
        'social': {
            'content': f'🚀 {prompt}\n\n#Marketing #Business #Success',
            'platform': 'twitter',
            'media_suggestions': ['Use engaging visuals', 'Include call-to-action']
        },
        'sms': {
            'content': f'Special offer! {prompt} Reply STOP to unsubscribe.',
            'character_count': 160
        },
        'blog': {
            'title': 'How to Succeed in Digital Marketing',
            'content': f'# Introduction\n\n{prompt}\n\n## Key Points\n\n- Point 1\n- Point 2\n- Point 3\n\n## Conclusion\n\nThank you for reading!',
            'seo_keywords': ['marketing', 'digital', 'success']
        }
    }
    
    generated_content = content_templates.get(content_type, content_templates['email'])
    
    # Store the generated content in the campaign
    if campaign_id in CAMPAIGNS_STORAGE:
        campaign = CAMPAIGNS_STORAGE[campaign_id]
        if 'content' not in campaign:
            campaign['content'] = []
        
        content_item = {
            'id': str(uuid.uuid4()),
            'type': content_type,
            'data': generated_content,
            'created_at': datetime.now().isoformat()
        }
        campaign['content'].append(content_item)
        campaign['updated_at'] = datetime.now().isoformat()
        CAMPAIGNS_STORAGE[campaign_id] = campaign
    
    return Response({
        'success': True,
        'content': generated_content,
        'content_type': content_type,
        'campaign_id': campaign_id,
        'generated_at': datetime.now().isoformat()
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def launch_campaign(request, campaign_id):
    """
    Launch a campaign.
    """
    # Update campaign status in storage
    if campaign_id in CAMPAIGNS_STORAGE:
        campaign = CAMPAIGNS_STORAGE[campaign_id]
        campaign['status'] = 'active'
        campaign['launched_at'] = datetime.now().isoformat()
        campaign['updated_at'] = datetime.now().isoformat()
        CAMPAIGNS_STORAGE[campaign_id] = campaign
    
    return Response({
        'success': True,
        'message': f'Campaign {campaign_id} has been launched successfully!',
        'campaign_id': campaign_id,
        'status': 'active',
        'launched_at': datetime.now().isoformat()
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def batch_generate_content(request, campaign_id):
    """
    Generate multiple content pieces for a campaign.
    """
    data = request.data
    content_types = data.get('content_types', ['email', 'social'])
    prompt = data.get('prompt', '')
    
    generated_contents = []
    for content_type in content_types:
        generated_contents.append({
            'content_type': content_type,
            'content': f'Generated {content_type} content based on: {prompt}',
            'status': 'generated'
        })
    
    return Response({
        'success': True,
        'contents': generated_contents,
        'campaign_id': campaign_id,
        'generated_at': datetime.now().isoformat()
    })