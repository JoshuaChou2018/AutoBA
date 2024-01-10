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
import time

def main(init_data_list, output_dir, init_goal_description, model_engine, openai_api, execute, blacklist):
    AIAgent = Agent(initial_data_list=init_data_list,
                    output_dir=output_dir,
                    initial_goal_description=init_goal_description,
                    model_engine=model_engine,
                    openai_api=openai_api,
                    execute=execute,
                    blacklist=blacklist)
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
                        help='model options: gpt-3.5-turbo (requires openai api), '
                             'gpt-3.5-turbo-1106 (requires openai api), '
                             'gpt-4 (requires openai api), '
                             'gpt-4-32k (requires openai api), '
                             'codellama-7bi, '
                             'codellama-13bi, '
                             'codellama-34bi,'
                             'llama2-7bc, '
                             'llama2-13bc, '
                             'llama2-70bc',
                        default='gpt-4')
    parser.add_argument('--execute',
                        help='execute code or only writing codes',
                        default=False,
                        type=bool)
    parser.add_argument('--blacklist',
                        help='list of softwares in blacklist, default: STAR,java,perl,annovar',
                        default='STAR,java,perl,annovar',
                        type=str)
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
    start_time = time.time()
    main(init_data_list, output_dir, init_goal_description, args.model, args.openai, args.execute, args.blacklist)
    end_time = time.time()
    print(f'\033[31m[Total time cost: {end_time-start_time}]\033[0m')

