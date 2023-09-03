#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：Auto-BioinfoGPT 
@File    ：app.py
@Author  ：Juexiao Zhou
@Contact : juexiao.zhou@gmail.com
@Date    ：2023/5/2 10:51 
'''

from src.agent import Agent
import yaml
import argparse

def main(init_data_list, output_dir, init_goal_description, model_engine, openai_api, excute):
    AIAgent = Agent(initial_data_list=init_data_list,
                    output_dir=output_dir,
                    initial_goal_description=init_goal_description,
                    model_engine=model_engine,
                    openai_api=openai_api,
                    excute=excute)
    AIAgent.run()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="ABC", add_help=False)
    parser.add_argument('--config',
                        help='path/to/config.yaml',
                        default='./examples/case1.1/config.yaml')
    parser.add_argument('--openai',
                        help='openai api',
                        default='SET_YOUR_OPENAI_API')
    parser.add_argument('--model',
                        help='openai model',
                        default='gpt-4')
    parser.add_argument('--excute',
                        help='excute code or only writing codes',
                        default=False,
                        type=bool)
    args = parser.parse_args()

    print("""

  /$$$$$$              /$$               /$$$$$$$   /$$$$$$ 
 /$$__  $$            | $$              | $$__  $$ /$$__  $$
| $$  \ $$ /$$   /$$ /$$$$$$    /$$$$$$ | $$  \ $$| $$  \ $$
| $$$$$$$$| $$  | $$|_  $$_/   /$$__  $$| $$$$$$$ | $$$$$$$$
| $$__  $$| $$  | $$  | $$    | $$  \ $$| $$__  $$| $$__  $$
| $$  | $$| $$  | $$  | $$ /$$| $$  | $$| $$  \ $$| $$  | $$
| $$  | $$|  $$$$$$/  |  $$$$/|  $$$$$$/| $$$$$$$/| $$  | $$
|__/  |__/ \______/    \___/   \______/ |_______/ |__/  |__/
                                                            
           Automated Bioinformatics Analysis
                  www.joshuachou.ink
    """)

    with open(args.config, 'r') as file:
        configs = yaml.safe_load(file)
    print(configs)
    init_data_list = configs['data_list']
    output_dir = configs['output_dir']
    init_goal_description = configs['goal_description']
    main(init_data_list, output_dir, init_goal_description, args.model, args.openai, args.excute)

