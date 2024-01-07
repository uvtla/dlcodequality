import torch
from torch.utils.data import Dataset, DataLoader
import json
import sqlite3


def read_jsonl_files(file_paths, suff):
    data = []
    for file_path in file_paths:
        with open(f'{file_path}{suff}.jsonl', 'r') as file:
            for line in file:
                data.append(json.loads(line))
    return data



class SQLiteCodeDataset(Dataset):
    def __init__(self, db_path, tokenizer, max_len, get_x, get_y):
        self.conn = sqlite3.connect(db_path)
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.get_x = get_x
        self.get_y = get_y

    def __len__(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM data")
        length, = cursor.fetchone()
        return length

    def __getitem__(self, idx):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM data LIMIT 1 OFFSET ?", (idx,))
        item = cursor.fetchone()
        cursor.close()

        encoding = self.tokenizer.encode_plus(
            self.get_x(item),
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True,
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.FloatTensor(self.get_y(item))
        }

    def close(self):
        self.conn.close()

class CodeDataset(Dataset):
    def __init__(self, file_paths, suff, tokenizer, max_len, get_x, get_y):
        self.tokenizer = tokenizer
        self.data = read_jsonl_files(file_paths, suff)
        self.max_len = max_len
        self.get_x = get_x
        self.get_y = get_y

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        encoding = self.tokenizer.encode_plus(
            self.get_x(item),
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True,
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.FloatTensor(self.get_y(item))
        }
        
class ReadyCodeDataset(CodeDataset):
    def __init__(self, file_paths, tokenizer, max_len):
        super().__init__(file_paths, '-ready', tokenizer, max_len, lambda x: x[0], lambda x: x[1])