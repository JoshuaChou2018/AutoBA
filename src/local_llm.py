# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.

from typing import Optional
import fire
from llama import Llama

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


if __name__ == "__main__":
    import os
    import torch.distributed as dist
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '5678'
    dist.init_process_group(backend='nccl', init_method='env://', rank=0, world_size=1)

    generator = api_preload(ckpt_dir='codellama-main/CodeLlama-7b-Instruct/',
                            tokenizer_path='codellama-main/CodeLlama-7b-Instruct/tokenizer.model')
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