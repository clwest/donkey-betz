# Generated migration for Session 677: Agent-Model Routing
# Creates AgentModelConfig, ModelPerformanceLog, ModelTrainingRun tables

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0140_session_642_agentexecution_user_nullable'),
    ]

    operations = [
        # AgentModelConfig - Maps agents to their optimal ML models
        migrations.CreateModel(
            name='AgentModelConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agent_name', models.CharField(db_index=True, help_text="Name of the agent (e.g., 'ResearchAgent', 'StockAnalystAgent')", max_length=100, unique=True)),
                ('category', models.CharField(choices=[('time_series', 'Time-Series Agents'), ('semantic', 'Semantic/Text Agents'), ('anomaly', 'Anomaly/Security Agents'), ('decision', 'Decision/Optimization Agents'), ('clustering', 'Segmentation/Clustering Agents'), ('general', 'General Purpose Agents')], default='general', help_text='Agent category for grouping similar agents', max_length=20)),
                ('primary_model', models.CharField(choices=[('lightgbm', 'LightGBM (Gradient Boosting)'), ('xgboost', 'XGBoost (Gradient Boosting)'), ('random_forest', 'Random Forest'), ('isolation_forest', 'Isolation Forest (Anomaly)'), ('kmeans', 'K-Means Clustering'), ('mlp', 'MLP Neural Network'), ('distilbert', 'DistilBERT (Sentiment)'), ('embeddings', 'OpenAI Embeddings'), ('cosine_similarity', 'Cosine Similarity'), ('rules', 'Rule-Based Heuristics'), ('lstm', 'LSTM (Time Series)'), ('prophet', 'Prophet (Seasonal)'), ('gnn', 'Graph Neural Network'), ('autoencoder', 'VAE Autoencoder'), ('rl', 'Reinforcement Learning'), ('dbscan', 'DBSCAN Clustering'), ('transformer', 'Small Transformer')], default='lightgbm', help_text='Primary ML model for this agent', max_length=50)),
                ('secondary_model', models.CharField(blank=True, choices=[('lightgbm', 'LightGBM (Gradient Boosting)'), ('xgboost', 'XGBoost (Gradient Boosting)'), ('random_forest', 'Random Forest'), ('isolation_forest', 'Isolation Forest (Anomaly)'), ('kmeans', 'K-Means Clustering'), ('mlp', 'MLP Neural Network'), ('distilbert', 'DistilBERT (Sentiment)'), ('embeddings', 'OpenAI Embeddings'), ('cosine_similarity', 'Cosine Similarity'), ('rules', 'Rule-Based Heuristics'), ('lstm', 'LSTM (Time Series)'), ('prophet', 'Prophet (Seasonal)'), ('gnn', 'Graph Neural Network'), ('autoencoder', 'VAE Autoencoder'), ('rl', 'Reinforcement Learning'), ('dbscan', 'DBSCAN Clustering'), ('transformer', 'Small Transformer')], default='rules', help_text='Secondary ML model for ensemble (optional)', max_length=50)),
                ('tertiary_model', models.CharField(blank=True, choices=[('lightgbm', 'LightGBM (Gradient Boosting)'), ('xgboost', 'XGBoost (Gradient Boosting)'), ('random_forest', 'Random Forest'), ('isolation_forest', 'Isolation Forest (Anomaly)'), ('kmeans', 'K-Means Clustering'), ('mlp', 'MLP Neural Network'), ('distilbert', 'DistilBERT (Sentiment)'), ('embeddings', 'OpenAI Embeddings'), ('cosine_similarity', 'Cosine Similarity'), ('rules', 'Rule-Based Heuristics'), ('lstm', 'LSTM (Time Series)'), ('prophet', 'Prophet (Seasonal)'), ('gnn', 'Graph Neural Network'), ('autoencoder', 'VAE Autoencoder'), ('rl', 'Reinforcement Learning'), ('dbscan', 'DBSCAN Clustering'), ('transformer', 'Small Transformer')], default='', help_text='Tertiary ML model for complex ensembles (optional)', max_length=50)),
                ('model_weights', models.JSONField(default=dict, help_text="Weights for model ensemble, e.g., {'lightgbm': 0.6, 'rules': 0.4}")),
                ('custom_params', models.JSONField(default=dict, help_text='Custom parameters for model configuration')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this configuration is active')),
                ('use_fallback', models.BooleanField(default=True, help_text='Fall back to default model on error')),
                ('fallback_model', models.CharField(choices=[('lightgbm', 'LightGBM (Gradient Boosting)'), ('xgboost', 'XGBoost (Gradient Boosting)'), ('random_forest', 'Random Forest'), ('isolation_forest', 'Isolation Forest (Anomaly)'), ('kmeans', 'K-Means Clustering'), ('mlp', 'MLP Neural Network'), ('distilbert', 'DistilBERT (Sentiment)'), ('embeddings', 'OpenAI Embeddings'), ('cosine_similarity', 'Cosine Similarity'), ('rules', 'Rule-Based Heuristics'), ('lstm', 'LSTM (Time Series)'), ('prophet', 'Prophet (Seasonal)'), ('gnn', 'Graph Neural Network'), ('autoencoder', 'VAE Autoencoder'), ('rl', 'Reinforcement Learning'), ('dbscan', 'DBSCAN Clustering'), ('transformer', 'Small Transformer')], default='lightgbm', help_text='Model to use if primary fails', max_length=50)),
                ('performance_score', models.FloatField(default=0.0, help_text='Current performance score (0-100)')),
                ('total_predictions', models.IntegerField(default=0, help_text='Total predictions made with this config')),
                ('successful_predictions', models.IntegerField(default=0, help_text='Number of successful predictions')),
                ('avg_latency_ms', models.FloatField(default=0.0, help_text='Average prediction latency in milliseconds')),
                ('last_evaluated', models.DateTimeField(blank=True, help_text='When performance was last evaluated', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Agent Model Configuration',
                'verbose_name_plural': 'Agent Model Configurations',
                'db_table': 'agent_model_config',
            },
        ),

        # ModelPerformanceLog - Track model performance over time
        migrations.CreateModel(
            name='ModelPerformanceLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evaluation_date', models.DateTimeField(auto_now_add=True)),
                ('metric_name', models.CharField(choices=[('accuracy', 'Accuracy'), ('precision', 'Precision'), ('recall', 'Recall'), ('f1', 'F1 Score'), ('rmse', 'Root Mean Square Error'), ('mae', 'Mean Absolute Error'), ('r2', 'R-Squared'), ('auc', 'Area Under Curve'), ('latency', 'Inference Latency'), ('throughput', 'Predictions per Second')], help_text='Name of the performance metric', max_length=50)),
                ('metric_value', models.FloatField(help_text='Value of the metric')),
                ('sample_count', models.IntegerField(default=0, help_text='Number of samples used for evaluation')),
                ('model_version', models.CharField(blank=True, help_text='Version of the model evaluated', max_length=20)),
                ('metadata', models.JSONField(default=dict, help_text='Additional metadata about the evaluation')),
                ('config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performance_logs', to='core.agentmodelconfig')),
            ],
            options={
                'verbose_name': 'Model Performance Log',
                'verbose_name_plural': 'Model Performance Logs',
                'db_table': 'model_performance_log',
                'ordering': ['-evaluation_date'],
            },
        ),

        # ModelTrainingRun - Track model training sessions
        migrations.CreateModel(
            name='ModelTrainingRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_type', models.CharField(help_text="Type of model being trained (e.g., 'lightgbm', 'lstm')", max_length=50)),
                ('version', models.CharField(help_text="Model version string (e.g., 'v1.0', 'v2.3')", max_length=20)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, help_text='When training completed', null=True)),
                ('status', models.CharField(choices=[('queued', 'Queued'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='queued', max_length=20)),
                ('hyperparameters', models.JSONField(default=dict, help_text='Hyperparameters used for training')),
                ('metrics', models.JSONField(default=dict, help_text='Training and validation metrics')),
                ('training_samples', models.IntegerField(default=0, help_text='Number of training samples')),
                ('validation_samples', models.IntegerField(default=0, help_text='Number of validation samples')),
                ('model_path', models.CharField(blank=True, help_text='Path to saved model file', max_length=500)),
                ('error_message', models.TextField(blank=True, help_text='Error message if training failed')),
                ('notes', models.TextField(blank=True, help_text='Notes about this training run')),
                ('agent_configs', models.ManyToManyField(blank=True, help_text='Agent configurations this model serves', related_name='training_runs', to='core.agentmodelconfig')),
            ],
            options={
                'verbose_name': 'Model Training Run',
                'verbose_name_plural': 'Model Training Runs',
                'db_table': 'model_training_run',
                'ordering': ['-started_at'],
            },
        ),

        # Add indexes
        migrations.AddIndex(
            model_name='agentmodelconfig',
            index=models.Index(fields=['agent_name', 'is_active'], name='agent_model_agent_n_1a2b3c_idx'),
        ),
        migrations.AddIndex(
            model_name='agentmodelconfig',
            index=models.Index(fields=['category'], name='agent_model_categor_4d5e6f_idx'),
        ),
        migrations.AddIndex(
            model_name='agentmodelconfig',
            index=models.Index(fields=['primary_model'], name='agent_model_primary_7g8h9i_idx'),
        ),
        migrations.AddIndex(
            model_name='modelperformancelog',
            index=models.Index(fields=['config', 'evaluation_date'], name='model_perfo_config__a1b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='modelperformancelog',
            index=models.Index(fields=['metric_name', 'evaluation_date'], name='model_perfo_metric__d4e5f6_idx'),
        ),
        migrations.AddIndex(
            model_name='modeltrainingrun',
            index=models.Index(fields=['model_type', 'status'], name='model_train_model_t_g7h8i9_idx'),
        ),
        migrations.AddIndex(
            model_name='modeltrainingrun',
            index=models.Index(fields=['started_at'], name='model_train_started_j1k2l3_idx'),
        ),
    ]
