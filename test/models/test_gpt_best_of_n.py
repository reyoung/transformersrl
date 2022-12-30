import os
from typing import List, Union

import datasets
import torch.optim.optimizer
import tqdm
from torch.utils.data import DataLoader
from transformers import GPTNeoForCausalLM, AutoTokenizer

from transformersrl.models.gpt_best_of_n import GPTBestOfN
from transformersrl.datasets.best_of_n_collator import BestOfNCollator

SPECIAL_TOKEN = "<|end of req rsp|>"


def test_train_gpt_best_of_n():
    model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-125M")
    model = model.transformer
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-125M")
    tokenizer.add_tokens([SPECIAL_TOKEN])
    model.resize_token_embeddings(len(tokenizer))
    collator = BestOfNCollator(tokenizer, special_token=SPECIAL_TOKEN)
    path = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "sentimental", "data")
    ds = datasets.load_from_disk(path)
    dataloader = DataLoader(dataset=ds["train"], collate_fn=collator, batch_size=2)

    model = GPTBestOfN(base=model)
    device = torch.device("cpu")
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters())

    for _ in range(1):
        for i, (query, samples, best) in enumerate(tqdm.tqdm(dataloader)):
            loss = model(query=query.to(device), samples=samples.to(device), best=best.to(device))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            print(i + 1, loss)
            if i + 1 == 50:
                break
