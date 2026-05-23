import json
import pandas as pd

for conf in ['TAv4', 'TAv5', 'TAv6']:
    try:
        d = json.load(open(f'results/comparison_20260512_145550/{conf}/cv_run_1/intent_report.json'))
        fp = 0
        fn = 0
        tp = int(round(d['out_of_scope']['support'] * d['out_of_scope']['recall']))
        support = d['out_of_scope']['support']
        
        # FN is support - tp
        fn = support - tp
        
        # FP is anything else predicted as out_of_scope
        for k, v in d.items():
            if k not in ['out_of_scope', 'accuracy', 'macro avg', 'weighted avg', 'micro avg']:
                fp += v.get('confused_with', {}).get('out_of_scope', 0)
                
        print(f"{conf}: OOS TP={tp}, FN={fn}, FP={fp}")
    except Exception as e:
        print(f"Error {conf}: {e}")
