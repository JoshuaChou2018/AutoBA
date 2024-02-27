# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.

from typing import Optional
import fire
from llama import Llama
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, set_seed
import torch

def api_preload(
    ckpt_dir: str,
    tokenizer_path: str,
    max_seq_len: int = 512,
    max_batch_size: int = 8,
):
    print(">> start loading model")

    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
        model_parallel_size=1
    )
    print(">> model loaded")
    return generator

def api_generator(instructions,
                  generator,
                  temperature: float = 0.2,
                  top_p: float = 0.95,
                  max_gen_len: Optional[int] = None,):
    results = generator.chat_completion(
        instructions,  # type: ignore
        max_gen_len=max_gen_len,
        temperature=temperature,
        top_p=top_p,
    )
    return results

def api_preload_hf(
    ckpt_dir: str,
    tokenizer_path: str = None,
    max_seq_len: int = 512,
    max_batch_size: int = 8,
):
    print(">> start loading model")
    tokenizer = AutoTokenizer.from_pretrained(ckpt_dir, padding_side="left")
    model = AutoModelForCausalLM.from_pretrained(ckpt_dir)
    model.to('cuda')
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=0)
    print(">> model loaded")
    return generator

def api_generator_hf(instructions,
                  generator):
    _prompt = ''
    results = generator(instructions[0][0]['content'], renormalize_logits=True, do_sample=True, use_cache=True, max_new_tokens=10)

    return results

def main(
    ckpt_dir: str,
    tokenizer_path: str,
    temperature: float = 0.2,
    top_p: float = 0.95,
    max_seq_len: int = 512,
    max_batch_size: int = 8,
    max_gen_len: Optional[int] = None,
):
    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
    )

    instructions = [
        [
            {
                "role": "user",
                "content": "In Bash, how do I list all text files in the current directory (excluding subdirectories) that have been modified in the last month?",
            }
        ],
        [
            {
                "role": "user",
                "content": "What is the difference between inorder and preorder traversal? Give an example in Python.",
            }
        ],
        [
            {
                "role": "system",
                "content": "Provide answers in JavaScript",
            },
            {
                "role": "user",
                "content": "Write a function that computes the set of sums of all contiguous sublists of a given list.",
            }
        ],
    ]
    results = generator.chat_completion(
        instructions,  # type: ignore
        max_gen_len=max_gen_len,
        temperature=temperature,
        top_p=top_p,
    )

    for instruction, result in zip(instructions, results):
        for msg in instruction:
            print(f"{msg['role'].capitalize()}: {msg['content']}\n")
        print(
            f"> {result['generation']['role'].capitalize()}: {result['generation']['content']}"
        )
        print("\n==================================\n")

def test1():
    ckpt_dir = 'codellama-main/CodeLlama-7b-Instruct/'
    tokenizer_path = 'codellama-main/CodeLlama-7b-Instruct/tokenizer.model'

    generator = api_preload(ckpt_dir=ckpt_dir,
                            tokenizer_path=tokenizer_path)
    instructions = [
        [
            {
                "role": "user",
                "content": "What is the difference between inorder and preorder traversal? Give an example in Python.",
            }
        ],
    ]
    results = api_generator(instructions=instructions, generator=generator)
    for instruction, result in zip(instructions, results):
        for msg in instruction:
            print(f"{msg['role'].capitalize()}: {msg['content']}\n")
        print(
            f"> {result['generation']['role'].capitalize()}: {result['generation']['content']}"
        )
        print("\n==================================\n")

def test2():
    ckpt_dir = 'codellama-main/CodeLlama-7b-Instruct-hf/'
    tokenizer_path = 'codellama-main/CodeLlama-7b-Instruct-hf/'

    generator = api_preload_hf(ckpt_dir=ckpt_dir)
    instructions = [
        [
            {
                "role": "user",
                "content": "What is the difference between inorder and preorder traversal? Give an example in Python.",
            }
        ],
    ]
    results = api_generator_hf(instructions=instructions, generator=generator)
    print(results)
    for instruction, result in zip(instructions, results):
        for msg in instruction:
            print(f"{msg['role'].capitalize()}: {msg['content']}\n")
        print(
            f"> {result['generation']['role'].capitalize()}: {result['generation']['content']}"
        )
        print("\n==================================\n")

def api_preload_deepseek(
    ckpt_dir: str,
    tokenizer_path: str = None,):
    print(">> start loading model")
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
    generator = AutoModelForCausalLM.from_pretrained(ckpt_dir, trust_remote_code=True,
                                                 torch_dtype=torch.bfloat16).cuda()
    print(">> model loaded")
    return tokenizer, generator

def api_generator_deepseek(instructions,
                  tokenizer,
                  generator,
                  max_new_tokens = 512,
                  top_k = 50,
                  top_p = 0.95):
    messages = instructions[0]
    inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(generator.device)
    # tokenizer.eos_token_id is the id of <|EOT|> token
    outputs = generator.generate(inputs, max_new_tokens=max_new_tokens, do_sample=False, top_k=top_k, top_p=top_p, num_return_sequences=1,
                             eos_token_id=tokenizer.eos_token_id)
    content = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
    results = [
        {
        'generation': {
            'role': 'AI',
            'content': content
        }
        }
    ]
    return results

def test3():
    ckpt_dir = 'deepseek/deepseek-coder-7b-instruct-v1.5'
    tokenizer_path = 'deepseek/deepseek-coder-7b-instruct-v1.5'

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(ckpt_dir, trust_remote_code=True,
                                                 torch_dtype=torch.bfloat16).cuda()
    messages = [
        {'role': 'user', 'content': "write a quick sort algorithm in python."}
    ]
    inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)
    # tokenizer.eos_token_id is the id of <|EOT|> token
    outputs = model.generate(inputs, max_new_tokens=512, do_sample=False, top_k=50, top_p=0.95, num_return_sequences=1,
                             eos_token_id=tokenizer.eos_token_id)
    print(tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True))


if __name__ == "__main__":
    import os
    import torch.distributed as dist
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '5678'
    dist.init_process_group(backend='nccl', init_method='env://', rank=0, world_size=1)
    test3()

