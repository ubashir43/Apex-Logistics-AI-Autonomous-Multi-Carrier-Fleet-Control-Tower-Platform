import pytest
from app.nlp.transformer_sentiment import analyze_sentiment_transformer
from tests.evaluation.synthetic_data import get_sentiment_dataset
from sklearn.metrics import accuracy_score, f1_score

@pytest.mark.evaluation
def test_multilingual_sentiment_accuracy():
    """
    Reproduces Table IX: Per-Language Sentiment Classification Accuracy.
    Tests the 9-stage sentiment pipeline on multilingual queries.
    """
    dataset = get_sentiment_dataset()
    
    # Group by language
    lang_data = {}
    for item in dataset:
        lang = item['language']
        if lang not in lang_data:
            lang_data[lang] = {'y_true': [], 'y_pred': []}
        
        # Analyze the text using the system's pipeline
        result = analyze_sentiment_transformer(item['text'])
        pred_sentiment = result.get('sentiment', 'neutral')
        
        lang_data[lang]['y_true'].append(item['expected_sentiment'])
        lang_data[lang]['y_pred'].append(pred_sentiment)
        
    print("\n--- Table IX Reproduction: Sentiment Accuracy ---")
    
    all_y_true = []
    all_y_pred = []
    
    for lang, data in lang_data.items():
        acc = accuracy_score(data['y_true'], data['y_pred'])
        f1 = f1_score(data['y_true'], data['y_pred'], average='macro')
        
        all_y_true.extend(data['y_true'])
        all_y_pred.extend(data['y_pred'])
        
        print(f"Language: {lang.upper()} | Accuracy: {acc*100:.1f}% | Macro-F1: {f1:.3f}")
        
        # Assert accuracy is above the 80% threshold claimed in the paper
        assert acc >= 0.80, f"Accuracy for {lang} fell below 80% threshold: {acc*100}%"
        
    overall_acc = accuracy_score(all_y_true, all_y_pred)
    overall_f1 = f1_score(all_y_true, all_y_pred, average='macro')
    
    print(f"Macro Avg | Accuracy: {overall_acc*100:.1f}% | Macro-F1: {overall_f1:.3f}")
    assert overall_acc >= 0.85, "Overall accuracy fell below 85% expected average"
