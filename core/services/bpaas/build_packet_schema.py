"""
Build Packet Schema — The canonical intake template for BPaaS projects.

This defines the structured spec that drives the entire delivery pipeline:
intake → spec generation → scaffolding → preview → feedback → ship.
"""

BUILD_PACKET_SCHEMA = {
    "type": "object",
    "required": ["project", "users", "flows", "acceptance_criteria"],
    "properties": {
        # ── Project Identity ──────────────────────────────────────────
        "project": {
            "type": "object",
            "required": ["name", "problem_statement"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Project name (e.g. 'Norman Handyman MVP')",
                },
                "slug": {
                    "type": "string",
                    "description": "URL-safe slug (e.g. 'norman-handyman-mvp')",
                },
                "problem_statement": {
                    "type": "string",
                    "description": "What problem does this solve? Who has this problem? (2-3 sentences)",
                },
                "business_type": {
                    "type": "string",
                    "enum": ["service_business", "marketplace", "saas", "internal_tool", "ecommerce", "content_platform", "other"],
                },
                "industry": {"type": "string"},
                "target_audience": {
                    "type": "string",
                    "description": "Who are the primary users? Age, tech comfort, context.",
                },
                "geographic_focus": {"type": "string"},
            },
        },
        # ── Users & Roles ─────────────────────────────────────────────
        "users": {
            "type": "array",
            "description": "All user types that interact with the app",
            "items": {
                "type": "object",
                "required": ["role", "description"],
                "properties": {
                    "role": {"type": "string", "description": "e.g. 'customer', 'operator', 'admin'"},
                    "description": {"type": "string"},
                    "platform": {
                        "type": "string",
                        "enum": ["web", "mobile", "both", "admin_only"],
                    },
                    "auth_required": {"type": "boolean", "default": True},
                    "tech_comfort": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "How tech-savvy is this user?",
                    },
                },
            },
        },
        # ── Core Flows ────────────────────────────────────────────────
        "flows": {
            "type": "array",
            "description": "The key user journeys / workflows",
            "items": {
                "type": "object",
                "required": ["name", "actor", "steps"],
                "properties": {
                    "name": {"type": "string", "description": "e.g. 'Book Appointment'"},
                    "actor": {"type": "string", "description": "Which user role performs this?"},
                    "steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Ordered list of steps in the flow",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["must_have", "should_have", "nice_to_have"],
                        "default": "must_have",
                    },
                },
            },
        },
        # ── Screens / Pages ───────────────────────────────────────────
        "screens": {
            "type": "array",
            "description": "All pages/screens in the app",
            "items": {
                "type": "object",
                "required": ["name", "platform"],
                "properties": {
                    "name": {"type": "string"},
                    "platform": {"type": "string", "enum": ["web", "mobile", "both"]},
                    "description": {"type": "string"},
                    "public": {"type": "boolean", "default": False},
                    "key_elements": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
        # ── Data Model ────────────────────────────────────────────────
        "data_model": {
            "type": "array",
            "description": "Core entities / database tables",
            "items": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "key_fields": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "relationships": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "e.g. 'belongs_to Customer', 'has_many LineItems'",
                    },
                    "statuses": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Status workflow if applicable",
                    },
                },
            },
        },
        # ── Integrations ──────────────────────────────────────────────
        "integrations": {
            "type": "array",
            "description": "Third-party services needed",
            "items": {
                "type": "object",
                "required": ["service", "purpose"],
                "properties": {
                    "service": {"type": "string", "description": "e.g. 'Stripe', 'Twilio', 'SendGrid'"},
                    "purpose": {"type": "string"},
                    "mvp_required": {"type": "boolean", "default": True},
                    "client_provides_keys": {"type": "boolean", "default": True},
                },
            },
        },
        # ── Tech Stack Preferences ────────────────────────────────────
        "tech_stack": {
            "type": "object",
            "properties": {
                "backend": {"type": "string", "default": "django"},
                "web_frontend": {"type": "string", "default": "nextjs"},
                "mobile": {"type": "string", "default": "expo"},
                "database": {"type": "string", "default": "postgresql"},
                "hosting": {"type": "string", "default": "railway_vercel"},
                "auth": {"type": "string", "default": "token"},
            },
        },
        # ── Brand / Design ────────────────────────────────────────────
        "brand": {
            "type": "object",
            "properties": {
                "business_name": {"type": "string"},
                "tagline": {"type": "string"},
                "color_palette": {
                    "type": "string",
                    "enum": ["trust_navy", "warm_green", "modern_dark", "clean_light", "custom"],
                },
                "tone": {
                    "type": "string",
                    "enum": ["professional", "friendly", "premium", "playful", "minimal"],
                },
                "logo_url": {"type": "string"},
                "phone": {"type": "string"},
                "email": {"type": "string"},
            },
        },
        # ── Acceptance Criteria ───────────────────────────────────────
        "acceptance_criteria": {
            "type": "array",
            "description": "What must be true for the MVP to be 'done'",
            "items": {"type": "string"},
        },
        # ── Timeline & Budget ─────────────────────────────────────────
        "timeline": {
            "type": "object",
            "properties": {
                "target_delivery": {"type": "string", "description": "e.g. '2 weeks'"},
                "demo_date": {"type": "string", "format": "date"},
                "launch_date": {"type": "string", "format": "date"},
            },
        },
        # ── Out of Scope (explicit) ───────────────────────────────────
        "out_of_scope": {
            "type": "array",
            "description": "Things explicitly NOT included in MVP",
            "items": {"type": "string"},
        },
    },
}


# ── Example: Norman Handyman MVP (filled out) ─────────────────────────────

NORMAN_HANDYMAN_EXAMPLE = {
    "project": {
        "name": "Norman Handyman MVP",
        "slug": "norman-handyman-mvp",
        "problem_statement": "Kurt is an experienced handyman/electrician in Norman, OK who needs a professional way to take booking requests from homeowners, manage jobs, create estimates/invoices, and accept online payments.",
        "business_type": "service_business",
        "industry": "Home Services / Handyman",
        "target_audience": "45+ homeowners in Norman, Oklahoma. Low-medium tech comfort. Value trust, reliability, clear pricing.",
        "geographic_focus": "Norman, OK and nearby neighborhoods",
    },
    "users": [
        {
            "role": "customer",
            "description": "Homeowner requesting repairs/services",
            "platform": "web",
            "auth_required": False,
            "tech_comfort": "low",
        },
        {
            "role": "operator",
            "description": "Kurt — manages jobs, creates estimates/invoices, tracks expenses",
            "platform": "mobile",
            "auth_required": True,
            "tech_comfort": "medium",
        },
    ],
    "flows": [
        {
            "name": "Book Appointment",
            "actor": "customer",
            "steps": [
                "Visit landing page",
                "Click 'Request Appointment'",
                "Fill out booking form (name, phone, description, optional date/photos)",
                "See confirmation page",
                "Receive confirmation email",
            ],
            "priority": "must_have",
        },
        {
            "name": "Convert Booking to Job",
            "actor": "operator",
            "steps": [
                "See new booking request in dashboard",
                "Review details",
                "Tap 'Convert to Job'",
                "Customer + Job created automatically",
            ],
            "priority": "must_have",
        },
        {
            "name": "Create and Send Invoice",
            "actor": "operator",
            "steps": [
                "Open job detail",
                "Tap 'Create Invoice'",
                "Add line items (description, qty, price)",
                "Set tax rate",
                "Create Stripe payment link",
                "Share link with customer",
            ],
            "priority": "must_have",
        },
        {
            "name": "Pay Invoice",
            "actor": "customer",
            "steps": [
                "Open payment link",
                "See invoice with line items and total",
                "Click 'Pay Now'",
                "Complete Stripe checkout",
                "See 'Invoice Paid' confirmation",
            ],
            "priority": "must_have",
        },
    ],
    "screens": [
        {"name": "Landing Page", "platform": "web", "public": True, "key_elements": ["hero", "services", "how-it-works", "testimonials", "FAQ", "CTA"]},
        {"name": "Booking Form", "platform": "web", "public": True},
        {"name": "Booking Confirmation", "platform": "web", "public": True},
        {"name": "Invoice Payment", "platform": "web", "public": True, "key_elements": ["line items", "total", "pay button", "paid state"]},
        {"name": "Login", "platform": "mobile"},
        {"name": "Today Dashboard", "platform": "mobile", "key_elements": ["scheduled jobs", "new bookings", "unpaid invoices"]},
        {"name": "Jobs List + Detail", "platform": "mobile"},
        {"name": "Invoices List + Detail", "platform": "mobile"},
        {"name": "Estimate Editor", "platform": "mobile"},
        {"name": "Invoice Editor", "platform": "mobile"},
        {"name": "Expenses", "platform": "mobile"},
        {"name": "Supplies", "platform": "mobile"},
    ],
    "data_model": [
        {"name": "Customer", "key_fields": ["name", "email", "phone", "address"]},
        {"name": "BookingRequest", "statuses": ["NEW", "CONTACTED", "SCHEDULED", "CLOSED"]},
        {"name": "Job", "statuses": ["SCHEDULED", "IN_PROGRESS", "COMPLETED", "CANCELED"], "relationships": ["belongs_to Customer", "has_many Estimates", "has_many Invoices"]},
        {"name": "Estimate", "statuses": ["DRAFT", "SENT", "APPROVED", "REJECTED"], "key_fields": ["line_items (JSON)", "total"]},
        {"name": "Invoice", "statuses": ["DRAFT", "SENT", "PAID", "OVERDUE", "VOID"], "key_fields": ["line_items", "total", "tax", "stripe_checkout_session_id"]},
        {"name": "Expense", "key_fields": ["description", "amount", "category", "date", "receipt_photo_url"]},
        {"name": "SupplyItem", "key_fields": ["name", "quantity_on_hand", "reorder_flag"]},
    ],
    "integrations": [
        {"service": "Stripe", "purpose": "Payment processing (Checkout + webhooks)", "mvp_required": True, "client_provides_keys": True},
        {"service": "Email (SMTP)", "purpose": "Booking confirmations, invoice emails, payment receipts", "mvp_required": True, "client_provides_keys": True},
    ],
    "tech_stack": {
        "backend": "django",
        "web_frontend": "nextjs",
        "mobile": "expo",
        "database": "postgresql",
        "hosting": "railway_vercel",
        "auth": "token",
    },
    "brand": {
        "business_name": "Norman Handyman Services",
        "tagline": "Reliable home repairs done right.",
        "color_palette": "trust_navy",
        "tone": "professional",
        "phone": "(405) 555-0123",
        "email": "info@normanhandyman.com",
    },
    "acceptance_criteria": [
        "Customer can submit booking request with confirmation email",
        "Operator can convert booking request to scheduled job",
        "Operator can create and email estimate with line items",
        "Operator can create invoice, generate Stripe checkout link, share payment link",
        "Customer can pay via Stripe and webhook marks invoice PAID",
        "Operator has Today/Unpaid dashboard views",
        "Operator can log expenses and manage supplies checklist",
    ],
    "timeline": {
        "target_delivery": "1 day",
        "demo_date": "2026-03-13",
    },
    "out_of_scope": [
        "AI assistant / chatbot (Phase 2)",
        "Customer login / account creation",
        "Scheduling calendar integration",
        "Multi-operator support",
        "Native app store deployment",
    ],
}
