# FinGenius

PART 2 -

## Overview
{context.business_name} is a {context.business_type.value} application built with {context.tech_stack.value}.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation
```bash
git clone <repository>
cd {context.business_name.lower().replace(' ', '-')}
docker-compose up -d
```

### Development
```bash
docker-compose -f docker-compose.dev.yml up
```

## Features
{self._format_features(context.business_features)}

## Architecture
Built with:
- Backend: {context.tech_stack.value}
- Database: PostgreSQL
- Frontend: React

## API Documentation
API documentation is available at `/api/docs` when running in development mode.

## Testing
```bash
docker-compose run --rm backend pytest
docker-compose run --rm frontend npm test
```

## Deployment
See `deployment/README.md` for deployment instructions.

## License
Proprietary - All rights reserved
