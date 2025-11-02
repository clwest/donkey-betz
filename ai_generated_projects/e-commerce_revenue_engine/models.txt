#!/usr/bin/env python3
"""
Product Standalone Data Model
Auto-converted from Django Model
Build ID: auto_fixed
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

class Product:
    """
    Standalone Product class
    Auto-converted from Django Model
    """

    def __init__(self, **kwargs):
        self.id = str(uuid.uuid4())
        self.build_id = "auto_fixed"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        # Set attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        """Save/update the model"""
        self.updated_at = datetime.now()
        print(f"💾 Product saved: {self.id}")
        return self

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'build_id': self.build_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            **{k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        def json_serializer(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

        return json.dumps(self.to_dict(), indent=2, default=json_serializer)

    def __str__(self):
        return f"Product({self.id[:8]}...)"

    def __repr__(self):
        return f"Product(id='Product', build_id='auto_fixed')"

if __name__ == "__main__":
    # Test the model
    model = Product(
        name="Test Instance",
        description="Auto-converted from Django model"
    )

    print(f"✅ Created {model}")
    print(f"📄 JSON: {model.to_json()}")

    model.save()

# Auto-fixed: Converted from Django Model to standalone class
# Build: auto_fixed
# Fixed at: 2025-09-23T22:58:55.221022
