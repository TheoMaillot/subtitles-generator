from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import copy
from tqdm.auto import tqdm
import re

def dict_translation(input_dict: dict, input_language: str, output_language: str):

    translated_dict = copy.deepcopy(input_dict)

    model_name = f"facebook/nllb-200-distilled-600M"
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name, src_lang=input_language)

    for i, seg in tqdm(enumerate(input_dict)):
        inputs = tokenizer(seg['text'], return_tensors="pt")

        generated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(output_language),
            max_length=60
        )

        # Decode the text 
        raw_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        
        # Remove the "zh" prefix and any extra characters at the beginning (e.g., zh, zhung, zhh?, zh2...)
        # The regex looks for a "zh" at the beginning (^) followed by lowercase letters, commas, or question marks.
        cleaned_text = re.sub(r'^zh[a-z,\?\s]*', '', raw_text)
        
        # Save the cleaned-up text
        translated_dict[i]['text'] = cleaned_text.strip()

    return translated_dict