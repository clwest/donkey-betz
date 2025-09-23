Creating a content generation API using Django REST Framework involves setting up a Django project, creating an app, defining models, serializers, and viewsets, and implementing custom actions if necessary. Here's a step-by-step guide to achieve this:

### Step 1: Set Up Your Django Project

1. **Install Django and Django REST Framework**:
   ```bash
   pip install django djangorestframework
   ```

2. **Create a Django Project**:
   ```bash
   django-admin startproject content_generator
   cd content_generator
   ```

3. **Create a Django App**:
   ```bash
   python manage.py startapp api
   ```

4. **Add the App and REST Framework to Installed Apps**:
   In `settings.py`, update the `INSTALLED_APPS` list:
   ```python
   INSTALLED_APPS = [
       ...
       'rest_framework',
       'api',
   ]
   ```

### Step 2: Define Your Models

In `api/models.py`, define models for the content you want to generate. Here’s a simple example of a `Content` model:

```python
from django.db import models

class Content(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

### Step 3: Create Serializers

In `api/serializers.py`, create a serializer for the `Content` model:

```python
from rest_framework import serializers
from .models import Content

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'
```

### Step 4: Create ViewSets

In `api/views.py`, create a viewset for the `Content` model:

```python
from rest_framework import viewsets
from .models import Content
from .serializers import ContentSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        title = request.data.get('title', 'Default Title')
        body = request.data.get('body', 'Default body content.')

        # Here you can implement your content generation logic
        new_content = Content.objects.create(title=title, body=body)
        serializer = self.get_serializer(new_content)

        return Response(serializer.data, status=201)
```

### Step 5: Set Up URLs

In `api/urls.py`, set up the URL routing for your API:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContentViewSet

router = DefaultRouter()
router.register(r'content', ContentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

Then, include this URL configuration in the main `urls.py` of your project (`content_generator/urls.py`):

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
```

### Step 6: Migrate Your Database

Run the following commands to create the necessary database tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Run Your Server

Start your Django development server:

```bash
python manage.py runserver
```

### Step 8: Test the API

You can now test your API using tools like Postman or cURL.

1. **Create Content**:
   - **POST** `/api/content/generate/`
   ```json
   {
       "title": "My First Post",
       "body": "This is the body of my first post."
   }
   ```

2. **List Content**:
   - **GET** `/api/content/`

3. **Retrieve Specific Content**:
   - **GET** `/api/content/{id}/`

4. **Update Content**:
   - **PUT** `/api/content/{id}/`

5. **Delete Content**:
   - **DELETE** `/api/content/{id}/`

### Conclusion

You now have a basic content generation API set up with Django REST Framework. You can expand upon this by adding authentication, permissions, pagination, and more sophisticated content generation logic as needed.