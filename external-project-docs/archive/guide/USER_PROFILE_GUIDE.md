# User Profile Intelligence - User Guide
## How Your AI Learns About You (And How You Control It)

---

## 🤖 What Is Profile Intelligence?

Your AI assistant now automatically learns about you from your conversations, building a comprehensive profile that helps it provide more personalized and relevant responses. Think of it as your AI developing a memory of who you are, what you do, and how you prefer to communicate.

### Before vs After
**Before**: Every conversation starts from scratch
- "What's your name again?"
- "Where are you located?"
- "What technologies do you work with?"

**After**: Your AI knows you
- "Hi Sarah! How's the React project going?"
- "Since you're in Denver, you might like this tech meetup..."
- "Based on your Python expertise, here's an advanced approach..."

---

## 🔍 What Your AI Learns

### Automatically Detected Information

#### **Basic Information**
- **Your Name**: How you prefer to be addressed
- **Location**: Where you live or work
- **Profession**: Your job title and company
- **Skills**: Technologies and areas of expertise you mention

#### **Communication Preferences**
- **Style**: Whether you prefer formal, casual, or technical language
- **Learning**: How you like information presented (visual, hands-on, theoretical)
- **Pace**: Whether you want quick answers or detailed explanations

#### **Personal Context**
- **Current Projects**: What you're working on
- **Goals**: What you're trying to achieve
- **Challenges**: Problems you're facing
- **Interests**: Topics you're passionate about

#### **Relationships & Network**
- **People**: Important colleagues, friends, family (first names only)
- **Teams**: Groups you work with
- **Mentors**: People you learn from

#### **Behavioral Patterns**
- **Active Hours**: When you're most productive
- **Communication Style**: How you typically express yourself
- **Problem-Solving Approach**: How you tackle challenges
- **Emotional Patterns**: Stress indicators and positive triggers

---

## 🛡️ Your Privacy Controls

### Complete Control Over Your Profile

#### **Learning Controls**
- **Enable/Disable Learning**: Turn automatic fact extraction on/off
- **Profile Sharing**: Control whether AI uses your profile for responses
- **Fact Correction**: Edit or remove any incorrect information
- **Complete Reset**: Delete your entire profile and start over

#### **What You Can Control**
✅ **What information is stored**  
✅ **How information is used**  
✅ **Who can access your profile** (only you)  
✅ **When to delete information**  
✅ **How to correct mistakes**  

#### **What's Protected**
🔒 **Full names are shortened to first names only**  
🔒 **Sensitive information is automatically filtered**  
🔒 **Low-confidence facts are excluded**  
🔒 **Complete audit trail of all changes**  
🔒 **Easy fact correction and removal**  

---

## 📊 Understanding Your Profile

### Profile Completeness Score
Your profile has a completeness percentage that shows how much your AI knows about you:

- **0-25%**: Basic information only
- **25-50%**: Good foundation with some context
- **50-75%**: Rich profile with detailed context
- **75-100%**: Comprehensive understanding

### Confidence Levels
Each fact has a confidence score:
- **High (80-100%)**: Very reliable information
- **Medium (60-79%)**: Likely accurate
- **Low (40-59%)**: Needs verification
- **Very Low (<40%)**: Filtered out automatically

---

## 🔧 Managing Your Profile

### Viewing Your Profile

#### **Profile Summary** (Always Available)
```
GET /api/profile/summary/
```
Shows basic statistics without revealing personal details:
- Completeness percentage
- Number of facts learned
- Privacy settings status
- Last update time

#### **Full Profile Details** (If Sharing Enabled)
```
GET /api/profile/details/
```
Complete profile information organized by category:
- Basic information
- Professional context
- Personal preferences
- Current projects and goals
- Behavioral patterns

### Updating Privacy Settings

#### **Change Learning Preferences**
```json
POST /api/profile/settings/
{
  "fact_learning_enabled": true,      // Allow AI to learn from conversations
  "profile_sharing_enabled": true,    // Allow AI to use profile in responses
  "communication_style": "casual",    // preferred, casual, formal, technical
  "learning_style": "hands-on"        // visual, hands-on, theoretical, practical
}
```

### Correcting Information

#### **Fix Incorrect Facts**
```json
POST /api/profile/correct-fact/
{
  "fact_key": "occupation",
  "action": "correct",
  "new_value": "Senior Software Engineer"
}
```

#### **Remove Unwanted Facts**
```json
POST /api/profile/correct-fact/
{
  "fact_key": "unwanted_skill",
  "action": "remove"
}
```

### Data Export & Deletion

#### **Download Your Data**
```
POST /api/profile/export/
```
Downloads complete profile in JSON format including:
- All profile information
- Extracted facts with sources
- Processing history
- Privacy settings

#### **Reset Your Profile**
```json
POST /api/profile/reset/
{
  "confirmation": "DELETE_MY_PROFILE"
}
```
**⚠️ Warning**: This permanently deletes all profile data!

---

## 🎯 How AI Uses Your Profile

### Personalized Responses

#### **Name Recognition**
- Uses your preferred name instead of generic "you"
- Remembers nicknames and variations

#### **Context Awareness**
- References your current projects
- Builds on your known expertise
- Considers your goals and challenges

#### **Communication Style**
- Adapts language to your preferences
- Matches your formality level
- Uses your preferred explanation style

#### **Relevant Information**
- Surfaces facts related to your query
- Connects to your existing knowledge
- Suggests based on your interests

### Example Personalization

#### **Query**: "Help me optimize this Python function"

**Without Profile**:
> "Here's a general approach to optimizing Python functions..."

**With Profile** (knowing you're experienced):
> "Hi Sarah! Since you're working with large datasets in your ML project, here's an advanced optimization using NumPy vectorization..."

---

## 📈 Profile Building Process

### How Facts Are Extracted

#### **Automatic Processing**
Every user message is analyzed for:
1. **Direct statements**: "My name is John"
2. **Contextual clues**: "I work at Google"
3. **Behavioral patterns**: Communication style, timing
4. **Relationship mentions**: "My colleague Sarah"
5. **Project references**: "I'm building an app"

#### **Confidence Scoring**
Each fact receives a confidence score based on:
- **Directness**: Explicit vs implied information
- **Frequency**: How often it's mentioned
- **Consistency**: Agreement with other facts
- **Recency**: How recent the information is

#### **Validation Process**
1. **Pattern matching** against 100+ extraction rules
2. **Confidence calculation** using multiple factors
3. **Conflict resolution** with existing facts
4. **User validation** for corrections

### Profile Evolution

#### **Immediate Learning** (After Each Message)
- Basic facts extracted and stored
- Profile updated in real-time
- Completeness score recalculated

#### **Pattern Analysis** (Every 10 Conversations)
- Communication style assessment
- Behavioral pattern identification
- Expertise area mapping
- Learning preference detection

#### **Profile Refinement** (Ongoing)
- Confidence scores adjusted
- Conflicting facts resolved
- User corrections incorporated
- Obsolete information filtered

---

## 🔍 Advanced Features

### Profile Analytics

#### **View Learning Statistics**
```
GET /api/profile/analytics/
```
Returns insights about your profile:
- Facts by category breakdown
- Extraction quality metrics
- Recent learning activity
- Processing performance

#### **Fact History**
```
GET /api/profile/facts/
```
Browse all extracted facts organized by:
- Category (personal, professional, preferences)
- Confidence level
- Extraction date
- Validation status

### Bulk Profile Building

#### **Process Historical Conversations**
For new users or profile rebuilding:
```bash
# Build profile from all conversations
python manage.py build_user_profiles --user your_username

# Preview what would be processed
python manage.py build_user_profiles --user your_username --dry-run

# View current profile statistics
python manage.py build_user_profiles --stats
```

---

## ⚠️ Important Privacy Notes

### What's Never Stored
- **Passwords or authentication details**
- **Financial information**
- **Health records**
- **Private documents or files**
- **Full conversations** (only extracted facts)

### What's Automatically Protected
- **Full names reduced to first names**
- **Addresses kept at city/state level**
- **Phone numbers and emails excluded**
- **Private company information filtered**
- **Confidential project details protected**

### Your Rights
- **Right to Know**: See exactly what AI knows about you
- **Right to Correct**: Fix any incorrect information
- **Right to Delete**: Remove specific facts or entire profile
- **Right to Export**: Download all your data
- **Right to Opt-Out**: Disable learning entirely

---

## 🚀 Getting Started

### First-Time Setup

1. **Enable Profile Learning** (Default: On)
   - Go to profile settings
   - Confirm learning preferences
   - Set communication style

2. **Have Natural Conversations**
   - Use your name in introductions
   - Mention your work and interests
   - Discuss current projects
   - Be yourself!

3. **Review Your Profile** (After ~10 conversations)
   - Check profile summary
   - Correct any mistakes
   - Adjust privacy settings

4. **Experience Personalization**
   - Notice AI using your name
   - See contextual responses
   - Feel the improved relevance

### Best Practices

#### **For Better Learning**
- **Be natural**: Don't force information
- **Use names**: Mention people in context
- **Describe projects**: Share what you're working on
- **Express preferences**: State how you like to learn

#### **For Privacy**
- **Review regularly**: Check your profile monthly
- **Correct mistakes**: Fix errors immediately
- **Adjust settings**: Update as preferences change
- **Stay informed**: Understand what's being learned

---

## 🆘 Troubleshooting

### Common Questions

#### **Q: Why isn't my AI learning about me?**
A: Check that "Fact Learning" is enabled in your profile settings.

#### **Q: The AI got something wrong about me. How do I fix it?**
A: Use the fact correction endpoint to update or remove incorrect information.

#### **Q: Can I see what the AI knows about me?**
A: Yes! Use the profile details endpoint (requires sharing to be enabled).

#### **Q: How do I start over completely?**
A: Use the profile reset endpoint with the confirmation phrase.

#### **Q: Is my information secure?**
A: Yes. Your profile is private, encrypted, and only you can access it.

### Getting Help

If you need assistance:
1. **Check the API documentation** for technical details
2. **Review the privacy settings** for control options
3. **Use the export feature** to understand your data
4. **Contact support** for specific issues

---

## 🎉 Enjoy Your Personalized AI!

Your AI assistant is now equipped to understand you better and provide more relevant, helpful responses. The more you interact naturally, the better it becomes at assisting you with your specific needs and preferences.

Remember: You're always in control of what your AI learns and how it uses that information. The goal is to make your interactions more efficient and personalized while respecting your privacy completely.

---

**Happy chatting with your AI that knows you! 🤖✨**