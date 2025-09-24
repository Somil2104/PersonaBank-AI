#!/usr/bin/env bash
set -euo pipefail

echo "[1/6] Creating directories..."
mkdir -p src/data src/models src/recommender src/utils data models notebooks tests

echo "[2/6] Moving existing scripts if they exist..."
mv -v export_paysim_train_test.py src/data/ 2>/dev/null || true
mv -v baseline_model_paysim.py src/models/ 2>/dev/null || true
mv -v predict_paysim.py src/models/ 2>/dev/null || true
mv -v score_paysim_batch.py src/models/ 2>/dev/null || true

echo "[3/6] Ensuring .gitignore rules..."
if [ ! -f .gitignore ]; then touch .gitignore; fi
grep -qxF ".env" .gitignore || echo ".env" >> .gitignore
grep -qxF "data/" .gitignore || echo "data/" >> .gitignore
grep -qxF "models/" .gitignore || echo "models/" >> .gitignore
grep -qxF "*.parquet" .gitignore || echo "*.parquet" >> .gitignore
grep -qxF "*.joblib" .gitignore || echo "*.joblib" >> .gitignore
grep -qxF "*.pkl" .gitignore || echo "*.pkl" >> .gitignore
grep -qxF "*.pt" .gitignore || echo "*.pt" >> .gitignore
grep -qxF ".DS_Store" .gitignore || echo ".DS_Store" >> .gitignore

echo "[4/6] Writing utils modules..."
cat > src/utils/db.py << 'PY'
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()
def get_engine():
    host = os.getenv("POSTGRES_HOST","localhost")
    port = int(os.getenv("POSTGRES_PORT","5432"))
    user = os.getenv("POSTGRES_USER")
    pwd  = os.getenv("POSTGRES_PASSWORD")
    db   = os.getenv("POSTGRES_DB")
    return create_engine(f"postgresql://{user}:{pwd}@{host}:{port}/{db}")
PY

cat > src/utils/features.py << 'PY'
def transform_transaction(row):
    amt = float(row.get('amount', 0.0) or 0.0)
    obo = float(row.get('oldbalanceorg', 0.0) or 0.0)
    obd = float(row.get('oldbalancedest', 0.0) or 0.0)
    nbo = float(row.get('newbalanceorig', 0.0) or 0.0)
    nbd = float(row.get('newbalancedest', 0.0) or 0.0)
    t = row.get('type')
    return {
        'amount': amt,
        'amount_to_oldbalanceorg': (amt / obo) if obo else 0.0,
        'amount_to_oldbalancedest': (amt / obd) if obd else 0.0,
        'delta_origin': nbo - obo,
        'delta_dest': nbd - obd,
        'type_CASH_IN':   1 if t == 'CASH_IN' else 0,
        'type_CASH_OUT':  1 if t == 'CASH_OUT' else 0,
        'type_DEBIT':     1 if t == 'DEBIT' else 0,
        'type_PAYMENT':   1 if t == 'PAYMENT' else 0,
        'type_TRANSFER':  1 if t == 'TRANSFER' else 0,
    }
PY

echo "[5/6] Patching script paths if files exist..."
# Replace CSV paths to data/ and model paths to models/
patch_paths() {
  local f="$1"
  [ -f "$f" ] || return 0
  sed -i.bak \
    -e "s|read_csv('paysim_train.csv')|read_csv('data/paysim_train.csv')|g" \
    -e "s|read_csv(\"paysim_train.csv\")|read_csv(\"data/paysim_train.csv\")|g" \
    -e "s|read_csv('paysim_test.csv')|read_csv('data/paysim_test.csv')|g" \
    -e "s|read_csv(\"paysim_test.csv\")|read_csv(\"data/paysim_test.csv\")|g" \
    -e "s|to_csv('paysim_train.csv'|to_csv('data/paysim_train.csv'|g" \
    -e "s|to_csv(\"paysim_train.csv\"|to_csv(\"data/paysim_train.csv\"|g" \
    -e "s|to_csv('paysim_test.csv'|to_csv('data/paysim_test.csv'|g" \
    -e "s|to_csv(\"paysim_test.csv\"|to_csv(\"data/paysim_test.csv\"|g" \
    -e "s|load_model('paysim_xgb.json')|load_model('models/paysim_xgb.json')|g" \
    -e "s|load_model(\"paysim_xgb.json\")|load_model(\"models/paysim_xgb.json\")|g" \
    -e "s|open('paysim_xgb_meta.json')|open('models/paysim_xgb_meta.json')|g" \
    -e "s|open(\"paysim_xgb_meta.json\")|open(\"models/paysim_xgb_meta.json\")|g" \
    -e "s|save_model('paysim_xgb.json')|save_model('models/paysim_xgb.json')|g" \
    -e "s|save_model(\"paysim_xgb.json\")|save_model(\"models/paysim_xgb.json\")|g" \
    "$f"
  rm -f "$f.bak"
}
patch_paths src/data/export_paysim_train_test.py
patch_paths src/models/baseline_model_paysim.py
patch_paths src/models/predict_paysim.py
patch_paths src/models/score_paysim_batch.py

echo "[6/6] Done. Suggested next commands:"
echo " - git add -A && git commit -m 'repo structure: src/, data/, models/ + utils' && git push"
echo " - Run export:   python3 src/data/export_paysim_train_test.py"
echo " - Run training: python3 src/models/baseline_model_paysim.py"
echo " - Predict:      python3 src/models/predict_paysim.py"
echo " - Batch score:  python3 src/models/score_paysim_batch.py input.ndjson output.ndjson"
