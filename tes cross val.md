
**1. Test Baseline (Default):**

**Bash**

```
rasa test nlu --config configCP.yml --cross-validation --folds 5
```

**2. Test Eksperimen N-Gram (Sparse):**

**Bash**

```
rasa test nlu --config configTAv1.yml --cross-validation --folds 5
```

**3. Test Eksperimen Semantik (IndoBERT):**

**Bash**

```
rasa test nlu --config configTAv2.yml --cross-validation --folds 5
```

**4. Test Eksperimen Hybrid Standar:**

**Bash**

```
rasa test nlu --config configTAv3.yml --cross-validation --folds 5
```

**5. Test Eksperimen Ultimate Hybrid:**

**Bash**

```
rasa test nlu --config configTAv4.yml --cross-validation --folds 5
```
