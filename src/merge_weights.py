# -*- coding: utf-8 -*-
"""
@Time ： 2023/12/12 15:09
@Auth ： Juexiao Zhou
@File ：merge_weights.py
@IDE ：PyCharm
@Page: www.joshuachou.ink
"""

import os
import re
import torch
from tqdm.cli import tqdm

#path_70b = '/home/zhouj0d/Science/PID28.ABC/AutoBA/src/llama-main/llama-2-13b-chat/'
#path_70b = '/home/zhouj0d/Science/PID28.ABC/AutoBA/src/codellama-main/CodeLlama-13b-Instruct/'
path_70b = '/home/zhouj0d/Science/PID28.ABC/AutoBA/src/codellama-main/CodeLlama-34b-Instruct/'

# Which files are merged into one
#merge_groups = [[0,1]]
merge_groups = [[0,1,2,3]]

weights = {
  int(fn.split('.')[1]): torch.load(f'{path_70b}{fn}', map_location=torch.device('cpu'))
  for fn in tqdm(sorted(os.listdir(path_70b)))
  if fn.endswith('.pth')
}

# These tensors are duplicated rather than distributed among the files

not_distributed = {
  k
  for k in weights[0].keys()
  #if all((weights[0][k] == weights[i][k]).min() for i in range(1,2))
  if all((weights[0][k] == weights[i][k]).min() for i in range(1,4))
}

# What tensor dimensions should be merged, based on whether they are implemented
# as Embedding, Row or Column Parallel.

merge_dimensions ={
  r'^layers.\d+.attention.wq.weight$': 0,
  r'^layers.\d+.attention.wk.weight$': 0,
  r'^layers.\d+.attention.wv.weight$': 0,
  r'^layers.\d+.attention.wo.weight$': 1,

  r'^tok_embeddings.weight$': 1,

  r'^layers.\d+.feed_forward.w1.weight$': 0,
  r'^layers.\d+.feed_forward.w2.weight$': 1,
  r'^layers.\d+.feed_forward.w3.weight$': 0,
  r'^output.weight$': 0
}

# Merging (or copying if not distributed)
output_weights = {}
for output, group in enumerate(merge_groups):
  output_weights[output] = dict()
  for name in tqdm(weights[group[0]], leave=False):
    if name in not_distributed:
      output_weights[output][name] = weights[0][name]
    else:
      axis = next(axis for exp, axis in merge_dimensions.items() if re.match(exp, name))
      output_weights[output][name] = torch.cat([
          weights[member][name]
          for member in group
      ], axis=axis)

os.makedirs(f'{path_70b}/one-gpu/', exist_ok=True)
with open(f'{path_70b}/params.json') as fin:
  with open(f'{path_70b}/one-gpu/params.json', 'w') as fout:
    fout.write(fin.read())

torch.save(
    output_weights[0],
    f'{path_70b}/one-gpu/consolidated.00.pth'
)