# Field Usage Analysis

## Summary


### Timestamp Variants

#### `created_at`
- **Total occurrences**: 446
- **Files searched**: 887
- **Usage patterns**:
  - order_by: 170
  - serializer_field: 126
  - attribute_access: 81
  - raw_sql_select: 29
  - filter: 24
  - values: 5
  - serializer_definition: 4
  - kwarg: 4
  - F_expression: 2
  - Q_expression: 1
- **Examples**:
  - `verify_stack_details.py:16` - order_by
  - `investigate_350_myth.py:130` - order_by
  - `investigate_350_myth.py:150` - order_by

#### `started_at`
- **Total occurrences**: 54
- **Files searched**: 887
- **Usage patterns**:
  - order_by: 38
  - attribute_access: 10
  - serializer_field: 3
  - filter: 2
  - F_expression: 1
- **Examples**:
  - `cleanup_stock_scout_spam.py:31` - order_by
  - `investigate_agent_progress.py:16` - order_by
  - `verify_agent_orchestra.py:23` - order_by

#### `updated_at`
- **Total occurrences**: 46
- **Files searched**: 887
- **Usage patterns**:
  - serializer_field: 38
  - attribute_access: 4
  - assignment: 2
  - order_by: 2
- **Examples**:
  - `serializers.py:21` - serializer_field
  - `admin.py:15` - serializer_field
  - `admin.py:63` - serializer_field

#### `completed_at`
- **Total occurrences**: 39
- **Files searched**: 887
- **Usage patterns**:
  - assignment: 24
  - serializer_field: 5
  - attribute_access: 5
  - kwarg: 2
  - order_by: 2
  - F_expression: 1
- **Examples**:
  - `force_cleanup_stuck_tasks.py:68` - assignment
  - `cleanup_stock_scout_spam.py:72` - assignment
  - `clear_frontend_cache.py:46` - assignment

#### `ended_at`
- **Total occurrences**: 14
- **Files searched**: 887
- **Usage patterns**:
  - assignment: 6
  - order_by: 2
  - serializer_field: 2
  - kwarg: 2
  - filter: 2
- **Examples**:
  - `views.py:154` - order_by
  - `views.py:1096` - order_by
  - `search_registry_v2.py:109` - serializer_field

#### `start_time`
- **Total occurrences**: 10
- **Files searched**: 887
- **Usage patterns**:
  - raw_sql_select: 3
  - Q_expression: 2
  - assignment: 2
  - serializer_field: 1
  - order_by: 1
  - kwarg: 1
- **Examples**:
  - `claude_chatgpt_import_report.py:52` - Q_expression
  - `claude_chatgpt_import_report.py:108` - Q_expression
  - `views.py:2405` - raw_sql_select

#### `end_time`
- **Total occurrences**: 7
- **Files searched**: 887
- **Usage patterns**:
  - assignment: 5
  - raw_sql_select: 1
  - filter: 1
- **Examples**:
  - `views.py:2405` - raw_sql_select
  - `conftest.py:115` - assignment
  - `conftest.py:121` - assignment

#### `start_date`
- **Total occurrences**: 4
- **Files searched**: 887
- **Usage patterns**:
  - filter: 4
- **Examples**:
  - `views.py:81` - filter
  - `analyze_performance.py:178` - filter
  - `analyze_performance.py:276` - filter


### User Variants

#### `user`
- **Total occurrences**: 2051
- **Files searched**: 887
- **Usage patterns**:
  - kwarg: 1186
  - attribute_access: 302
  - filter: 251
  - serializer_field: 108
  - assignment: 104
  - raw_sql_select: 40
  - raw_sql_where: 26
  - Q_expression: 13
  - serializer_definition: 9
  - values: 8
  - exclude: 3
  - F_expression: 1
- **Examples**:
  - `investigate_350_myth.py:137` - attribute_access
  - `investigate_350_myth.py:141` - attribute_access
  - `investigate_350_myth.py:218` - values

#### `created_by`
- **Total occurrences**: 14
- **Files searched**: 887
- **Usage patterns**:
  - kwarg: 6
  - serializer_field: 4
  - filter: 1
  - raw_sql_where: 1
  - Q_expression: 1
  - exclude: 1
- **Examples**:
  - `views.py:380` - filter
  - `fix_orchestration_delete.py:72` - raw_sql_where
  - `test_dashboard_feed_queries.py:24` - kwarg

#### `submitted_by`
- **Total occurrences**: 1
- **Files searched**: 887
- **Usage patterns**:
  - serializer_field: 1
- **Examples**:
  - `serializers.py:84` - serializer_field


### Status Variants

#### `is_active`
- **Total occurrences**: 130
- **Files searched**: 887
- **Usage patterns**:
  - kwarg: 83
  - filter: 29
  - assignment: 8
  - serializer_field: 7
  - raw_sql_select: 1
  - raw_sql_where: 1
  - serializer_definition: 1
- **Examples**:
  - `reset_test_user.py:38` - assignment
  - `ai_code_generator.py:255` - kwarg
  - `ai_code_generator.py:255` - filter

#### `is_archived`
- **Total occurrences**: 4
- **Files searched**: 887
- **Usage patterns**:
  - kwarg: 2
  - assignment: 2
- **Examples**:
  - `views_stock_opportunities.py:41` - kwarg
  - `views_stock_opportunities.py:205` - assignment
  - `views_stock_opportunities.py:254` - kwarg

#### `is_enabled`
- **Total occurrences**: 1
- **Files searched**: 887
- **Usage patterns**:
  - serializer_field: 1
- **Examples**:
  - `ai_code_generator.py:275` - serializer_field

