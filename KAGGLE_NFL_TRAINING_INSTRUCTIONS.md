# NFL Model Training Instructions

## Quick Start: Train Your NFL Prediction Model

### Step 1: Download Dataset

1. **Go to Kaggle**: https://www.kaggle.com/datasets/tobycrabtree/nfl-scores-and-betting-data
2. **Click "Download"** (requires free Kaggle account)
3. **Extract the ZIP** - you'll get `spreadspoke_scores.csv`
4. **Move CSV to**: `/tmp/nfl_data/spreadspoke_scores.csv`

```bash
# Create directory
mkdir -p /tmp/nfl_data

# After downloading from Kaggle, move it:
# mv ~/Downloads/spreadspoke_scores.csv /tmp/nfl_data/
```

### Step 2: Import Historical Data

Import games from 2018-present (recommended for modern NFL):

```bash
python manage.py import_nfl_historical_data --start-season 2018
```

**Options:**
- `--start-season 2010` - Get more data (2010-present)
- `--start-season 2018` - Recent data only (faster, cleaner)
- `--limit 100` - Test with just 100 games

**Expected output:**
```
✅ Import complete!
  Imported: 544 games (from 2018-2024)
  Skipped: 22 games
  Errors: 3 rows
```

### Step 3: Train Model

```bash
python manage.py train_nfl_model
```

**Expected output:**
```
Found 544 completed games
✅ Extracted 544 training examples

Train set: 435 games
Test set: 109 games

🚀 Training model...
✅ Model training complete!

==================================================
Test Accuracy: 67.89%
==================================================

📈 Model Performance:
  Model accuracy: 67.89%
  Baseline (always home): 56.88%
  Improvement: +11.0 percentage points

✅ Model saved successfully!
```

### Step 4: Test Predictions

```bash
python manage.py shell << 'EOF'
from ml.core.ml_engine import MLEngine
from sports.models import Game

ml_engine = MLEngine()
game = Game.objects.filter(league__sport_type='nfl', status='scheduled').first()

if game:
    print(f"\nPredicting: {game.away_team.name} @ {game.home_team.name}")
    prediction = ml_engine.predict_nfl_game(str(game.id))

    print(f"Winner: {prediction['winner']}")
    print(f"Confidence: {prediction['confidence']:.1%}")
    print(f"Model: {prediction['model_used']}")  # Should say "sports_crypto_lstm" not "baseline"
EOF
```

---

## What You Get

### Dataset Coverage
- **Years**: 1966-2013+ (use 2018+ for modern NFL)
- **Games**: 500+ per season (544 from 2018-2024)
- **Data**: Scores, dates, teams, betting lines

### Model Performance
- **Expected Accuracy**: 60-70% (better than 57% baseline)
- **Home Field Advantage**: Automatically learned from data
- **Team Strength**: Based on last 10 games
- **Features**: 8 engineered features per game

### Trained Model Output
```python
{
    'winner': 'Kansas City Chiefs',
    'confidence': 0.73,
    'home_win_probability': 0.68,
    'predicted_spread': 4.2,
    'model_used': 'sports_crypto_lstm',  # ✅ Now trained!
    'key_factors': [
        'Chiefs strong offense (avg 28.4 PPG)',
        'Chiefs superior defense',
        'Home field advantage'
    ],
    'recommendation': {
        'recommended_bets': [
            {'bet_type': 'moneyline', 'selection': 'Chiefs', 'confidence': 0.73},
            {'bet_type': 'spread', 'selection': 'Chiefs -4.2', 'confidence': 0.73}
        ],
        'confidence_level': 'moderate'
    }
}
```

---

## Troubleshooting

### Issue: "File not found"
**Solution**: Make sure CSV is at `/tmp/nfl_data/spreadspoke_scores.csv`

### Issue: "Teams not found"
**Solution**: Run `python manage.py sync_nfl_teams` first

### Issue: "Not enough data to train"
**Solution**: Lower `--start-season` to get more games (e.g., `--start-season 2010`)

### Issue: Low accuracy (< 55%)
**Solution**:
- Import more historical data (lower start-season)
- Check if team names are matching correctly
- Verify scores imported properly

---

## Advanced: Improve Model

### Option 1: More Data
```bash
# Get 10+ years of data
python manage.py import_nfl_historical_data --start-season 2010
python manage.py train_nfl_model
```

### Option 2: Add More Features
Edit `ml/core/ml_engine.py` → `_extract_nfl_game_features()`:
- Add weather data
- Add injury reports
- Add betting line movement
- Add rest days
- Add division rivalry indicator

### Option 3: Better Model
Replace MLPRegressor with:
- XGBoost
- LightGBM
- Neural network with more layers
- Ensemble of multiple models

---

## Next Steps After Training

1. **Frontend Integration** (Session 15)
   - Display predictions in Sports Hub
   - Show confidence levels
   - Add betting slip

2. **Live Updates** (Session 15-16)
   - Real-time prediction updates
   - Model retraining weekly
   - Track prediction accuracy

3. **User Features** (Session 16+)
   - Save favorite teams
   - Custom betting strategies
   - Performance tracking

---

## Dataset Info

**Source**: Kaggle - Toby Crabtree
**URL**: https://www.kaggle.com/datasets/tobycrabtree/nfl-scores-and-betting-data
**License**: Public domain
**Size**: ~250KB
**Records**: 10,000+ games
**Quality**: High (maintained dataset)

**Columns** (typical):
- `schedule_date` - Game date
- `schedule_season` - Season year
- `schedule_week` - Week number
- `team_home` - Home team name
- `team_away` - Away team name
- `score_home` - Home team score
- `score_away` - Away team score
- `spread_favorite` - Betting spread
- `over_under_line` - Total points line
- `weather_temperature` - Game temperature
- `weather_wind_mph` - Wind speed

---

Ready to train! 🚀