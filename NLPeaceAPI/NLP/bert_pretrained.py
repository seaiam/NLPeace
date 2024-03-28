import pandas as pd
import tensorflow as tf
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler, RandomSampler
from sklearn.model_selection import train_test_split
import os
import numpy as np
import tqdm
import nltk
import re
import string
from nltk.corpus import stopwords
import spacy
import torch
from tqdm import trange
from sklearn.metrics import precision_score, recall_score, f1_score
from transformers import RobertaForSequenceClassification, RobertaTokenizer
import torch.optim as optim
from transformers import get_linear_schedule_with_warmup
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer

def import_data():
    df = pd.read_csv('data/labeled_data.csv')
    # Keep only the 'tweet' and 'class' columns
    df = df[['tweet', 'class']]
    return df

def preprocess(text):
    # Remove Twitter handles
    text = re.sub(r'@\w+', '', text)
    # Tokenize the text
    #words = nltk.word_tokenize(text)
    # Convert to lowercase
    #words = [word.lower() for word in words]
    # Remove stopwords
    #words = [word for word in words if word not in stop_words]
    # Remove punctuation
    #words = [word for word in words if word not in string.punctuation]
    # Lemmatize the words
    #doc = nlp(" ".join(words))
    #words = [token.lemma_ for token in doc]
    return text

def process_data(df):
    df['processed_tweet'] = df['tweet'].apply(preprocess)
    return df

# Download the stopwords from NLTK
#nltk.download('stopwords')
#nltk.download('punkt')
# Download SpaCy resources
#spacy.cli.download('en_core_web_sm')
# Initialize SpaCy's English tokenizer and lemmatizer
#nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

# Initialize NLTK's English stopwords
#stop_words = set(stopwords.words('english'))

"""read and preprocess data"""

#Load data
df = pd.read_csv('data/labeled_data.csv', usecols=['class', 'tweet'])

# Preprocess tweets
df['processed_tweet'] = df['tweet'].apply(preprocess)

df['label'] = df['class']
df['label'] = df['label'].map(lambda x: 1 if x == 2 else x)

#extract tweet and class values
tweets = df.processed_tweet.values
labels = df.label.values

#tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case = True)
#tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

token_id = []
attention_masks = []

def preprocessing(text, tokenizer):
  return tokenizer.encode_plus(
      text,
      add_special_tokens = True,
      max_length = 280,
      padding='max_length',
      truncation=True,
      return_attention_mask = True,
      return_tensors = 'pt'
  )

for tweet in tweets:
  encoding_dict = preprocessing(tweet, tokenizer)
  token_id.append(encoding_dict['input_ids'])
  attention_masks.append(encoding_dict['attention_mask'])

token_id = torch.cat(token_id, dim = 0)
attention_masks = torch.cat(attention_masks, dim = 0)
labels = torch.tensor(labels)

batch_size = 16

train_idx, test_idx = train_test_split(
    np.arange(len(labels)),
    test_size = 0.2,
    shuffle = True,
    stratify = labels
)

train_set = TensorDataset(token_id[train_idx], attention_masks[train_idx], labels[train_idx])
test_set = TensorDataset(token_id[test_idx], attention_masks[test_idx], labels[test_idx])

train_dataloader = DataLoader(
    train_set,
    sampler = RandomSampler(train_set),
    batch_size = batch_size
)

test_dataloader = DataLoader(
    test_set,
    sampler = RandomSampler(test_set),
    batch_size = batch_size
)

epochs = 3
total_steps = len(train_dataloader) * epochs

#model = BertForSequenceClassification.from_pretrained(
 #   'bert-base-uncased',
  #  num_labels = 2,
   # output_attentions = False,
    #output_hidden_states = False,
#)
#model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=2)
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)

#optimizer = torch.optim.AdamW(model.parameters(), lr = 5e-5, eps = 1e-08)
optimizer = optim.SGD(model.parameters(), lr=0.0001, momentum=0.9)
scheduler = get_linear_schedule_with_warmup(optimizer,
                                            num_warmup_steps=0,
                                            num_training_steps=total_steps)

model.cuda()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

for _ in trange(epochs, desc='Epoch'):
    model.train()
    tr_loss = 0
    num_tr_examples, num_tr_steps = 0, 0

    for step, batch in enumerate(train_dataloader):
        batch = tuple(t.to(device) for t in batch)
        inputs = {'input_ids': batch[0],
                  'attention_mask': batch[1],
                  'labels': batch[2]}
        optimizer.zero_grad()

        train_output = model(**inputs)
        train_output.loss.backward()
        optimizer.step()
        scheduler.step()  # Update learning rate

        tr_loss += train_output.loss.item()
        num_tr_examples += inputs['input_ids'].size(0)
        num_tr_steps += 1

    # Validation
    model.eval()
    eval_loss, eval_accuracy = 0, 0
    nb_eval_steps, nb_eval_examples = 0, 0
    total_correct, total_examples = 0, 0

    for batch in test_dataloader:
        batch = tuple(t.to(device) for t in batch)
        inputs = {'input_ids': batch[0],
                  'attention_mask': batch[1],
                  'labels': batch[2]}

        with torch.no_grad():
            eval_output = model(**inputs)
        logits = eval_output.logits
        loss = eval_output.loss
        eval_loss += loss.item()

        preds = torch.argmax(logits, dim=1)
        labels = inputs['labels']

        # Check for size mismatch before comparison
        if preds.size() == labels.size():
            total_correct += torch.sum(preds == labels).item()
            total_examples += len(labels)
        else:
            print("Warning: Size mismatch in batch. Skipping evaluation for this batch.")

        nb_eval_examples += inputs['input_ids'].size(0)
        nb_eval_steps += 1

    eval_loss = eval_loss / nb_eval_steps

    # Calculate accuracy only if at least one batch was evaluated
    if total_examples > 0:
        eval_accuracy = total_correct / total_examples
        print("Validation Loss: {}".format(eval_loss))
        print("Validation Accuracy: {}".format(eval_accuracy))
    else:
        print("No batches were evaluated. Check your data or model configuration.")

# Save the fine-tuned model
model_dir = 'models/'
if not os.path.exists(model_dir):
    os.makedirs(model_dir)
model_path = os.path.join(model_dir, 'fine_tuned_bert_model')
model.save_pretrained(model_path)
print("Saved fine-tuned BERT model at:", model_path)

# Saving directory
output_dir = './saved_model/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Save model
model_path = os.path.join(output_dir, 'bert_model_state.bin')
torch.save(model.state_dict(), model_path)

# Save tokenizer
tokenizer_path = os.path.join(output_dir, 'bert_tokenizer')
tokenizer.save_pretrained(tokenizer_path)