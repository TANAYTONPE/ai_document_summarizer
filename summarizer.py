from huggingface_hub import login


from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re
MODEL_NAME = "facebook/bart-large-cnn"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def split_text(text, chunk_size=800):

    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)

    return chunks


def summarize_chunk(chunk):

    inputs = tokenizer(
        chunk,
        return_tensors="pt",
        max_length=1024,
        truncation=True
    )

    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=150,
        min_length=40,
        length_penalty=2.0,
        num_beams=4,
        forced_bos_token_id=tokenizer.bos_token_id
    )

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def generate_summary(text):

    chunks = split_text(text)
    text = re.sub(r'\s+', ' ', text)     # remove extra spaces
    text = re.sub(r'[^a-zA-Z0-9., ]', '', text)   # remove weird symbols
    summaries = []

    for chunk in chunks:
        s = summarize_chunk(chunk)
        summaries.append(s)

    final_summary = " ".join(summaries)

    return final_summary