# Agent Execution System

This directory contains the active agent execution system that transforms
passive agent registrations into working, revenue-generating agents.

## Key Components

- `executors/`: Agent executor implementations
- `executor_registry.py`: Central executor management
- `models.py`: Django models for agent tracking

## Usage

1. Initialize executors: `python manage.py initialize_executors`
2. Run tests: `python test_real_agent_execution.py`
3. Demo system: `python demo_working_agents.py`

## Available Executors

- **IncomeBuilderExecutor**: Analyzes opportunities and creates action plans
- **ContentCreatorExecutor**: Generates AI-powered content
- **PaymentProcessorExecutor**: Handles invoicing and payments

## Key Features

- Real API integration (OpenAI, Stripe, web search)
- Actual file generation and deliverables
- Performance monitoring and cost tracking
- Error handling and retry logic
- Concurrent execution support
