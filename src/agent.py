#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：Auto-BioinfoGPT 
@File    ：agent.py
@Author  ：Juexiao Zhou
@Contact : juexiao.zhou@gmail.com
@Date    ：2023/5/3 13:24 
'''
import os.path
import os
import torch.cuda
from src.prompt import PromptGenerator
from src.spinner import Spinner
from src.local_llm import api_preload, api_generator
import openai
import time
import json
import subprocess

class CodeExecutor:
    def __init__(self):
        self.bash_code_path = None

    def execute(self, bash_code_path):

        self.bash_code_path = bash_code_path
        with open(self.bash_code_path, 'r') as input_file:
            bash_content = input_file.read()

        self.bash_code_path_execute = self.bash_code_path + '.execute.sh'

        # 打开新生成的 Bash 文件以供写入
        with open(self.bash_code_path_execute, 'w') as output_file:
            # 写入原始内容
            output_file.write(bash_content)
            # 在文件末尾添加打印特殊字符串的 Bash 命令
            special_string = "K7pJhFbA3NqW execute Success"
            output_file.write('\n')  # 确保在新行开始
            output_file.write(f'echo "{special_string}"')

        # 使用 subprocess 执行 Bash 文件，将输出捕获到一个字符串中
        process = subprocess.Popen(['bash', self.bash_code_path_execute],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            text=True)

        # 实时读取输出并打印
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        # 等待命令执行完毕
        process.communicate()

        if special_string in process.stdout:
            return True, 'Success'
        else:
            return False, process.stderr

class Agent:
    def __init__(self,initial_data_list, output_dir, initial_goal_description, model_engine, openai_api, execute = True, blacklist=''):
        self.initial_data_list = initial_data_list
        self.initial_goal_description = initial_goal_description
        self.tasks = []
        self.update_data_lists = [_ for _ in initial_data_list]
        self.output_dir = output_dir
        self.update_data_lists.append(f'{output_dir}: all outputs should be stored under this dir')
        self.generator = PromptGenerator(blacklist=blacklist)
        self.model_engine = model_engine
        self.valid_model_engines = ['gpt-3.5', 'gpt-4', 'codellama-7bi', 'codellama-13bi', 'codellama-34bi']
        self.global_round = 0
        self.execute = execute
        self.code_executor = CodeExecutor()
        openai.api_key = openai_api

        if self.model_engine not in self.valid_model_engines:
            print('[ERROR] model invalid, please check the model engine selected!')
            exit()

        # preload local model
        if 'codellama' in self.model_engine:
            import torch.distributed as dist
            os.environ['MASTER_ADDR'] = 'localhost'
            os.environ['MASTER_PORT'] = '5678'
            if torch.cuda.is_available():
                dist.init_process_group(backend='nccl', init_method='env://', rank=0, world_size=1)
            else:
                dist.init_process_group(backend='gloo', init_method='env://', rank=0, world_size=1)
        if self.model_engine == 'codellama-7bi':
            self.local_llm_generator = api_preload(ckpt_dir='src/codellama-main/CodeLlama-7b-Instruct/',
                                    tokenizer_path='src/codellama-main/CodeLlama-7b-Instruct/tokenizer.model',
                                    max_seq_len=4096)
        elif self.model_engine == 'codellama-13bi':
            self.local_llm_generator = api_preload(ckpt_dir='src/codellama-main/CodeLlama-13b-Instruct/',
                                    tokenizer_path='src/codellama-main/CodeLlama-13b-Instruct/tokenizer.model',
                                    max_seq_len=4096)
        elif self.model_engine == 'codellama-34bi':
            self.local_llm_generator = api_preload(ckpt_dir='src/codellama-main/CodeLlama-34b-Instruct/',
                                    tokenizer_path='src/codellama-main/CodeLlama-34b-Instruct/tokenizer.model',
                                    max_seq_len=4096)

    def get_single_response(self, prompt):

        # use openai
        if self.model_engine in ['gpt-3.5', 'gpt-4']:
            response = openai.ChatCompletion.create(
                model=self.model_engine,
                  messages=[
                    {"role": "user", "content": str(prompt)}],
                max_tokens=1024,
                temperature=0,
            )

            """
            {
              "choices": [
                {
                  "finish_reason": "stop",
                  "index": 0,
                  "message": {
                    "content": "Hello! As an AI language model, I don't have emotions, but I'm functioning well. I'm here to assist you with any questions or tasks you may have. How can I help you today?",
                    "role": "assistant"
                  }
                }
              ],
              "created": 1683014436,
              "id": "chatcmpl-7BfE4AdTo5YlSIWyMDS6nL6CYv5is",
              "model": "gpt-3.5-turbo-0301",
              "object": "chat.completion",
              "usage": {
                "completion_tokens": 42,
                "prompt_tokens": 20,
                "total_tokens": 62
              }
            }
            """

            response_message = response['choices'][0]['message']['content']
        elif self.model_engine in ['codellama-7bi', 'codellama-13bi', 'codellama-34bi']:
            instructions = [
                [
                    {
                        "role": "user",
                        "content": str(prompt),
                    }
                ],
            ]
            results = api_generator(instructions=instructions,
                                    generator=self.local_llm_generator,
                                    temperature=0.6)
            response_message = results[0]['generation']['content']
        return response_message

    def valid_json_response(self, response_message):
        if not os.path.isdir(f'{self.output_dir}'):
            os.makedirs(f'{self.output_dir}')
        try:
            with open(f'{self.output_dir}/{self.global_round}_response.json', 'w') as w:
                json.dump(eval(response_message), w)
            json.load(open(f'{self.output_dir}/{self.global_round}_response.json'))
        except:
            print('[INVALID RESSPONSE]\n', response_message)
            return False
        return True

    def process_tasks(self, response_message):
        self.tasks = response_message['plan']

    def execute_code(self, response_message):
        if not os.path.isdir(f'{self.output_dir}'):
            os.makedirs(f'{self.output_dir}')
        try:
            with open(f'{self.output_dir}/{self.global_round}.sh', 'w') as w:
                w.write(response_message['code'])
            if self.execute:
                execute_statu, execute_info = self.code_executor.execute(bash_code_path=f'{self.output_dir}/{self.global_round}.sh')
                #os.system(f'bash {self.output_dir}/{self.global_round}.sh')
                return execute_statu, execute_info
            return True, 'Success without executing'
        except Exception as e:
            return False, e

    def run_plan_phase(self):
        # initial prompt
        init_prompt = self.generator.get_prompt(
            data_list=self.initial_data_list,
            goal_description=self.initial_goal_description,
            global_round=self.global_round)

        self.generator.format_user_prompt(init_prompt, self.global_round)
        with Spinner(f'\033[32m[AI Thinking...]\033[0m'):
            response_message = self.get_single_response(init_prompt)
            while not self.valid_json_response(response_message):
                print(f'\033[32m[Invalid Response, Waiting for 20s and Retrying...]\033[0m')
                print(f'invalid response: {response_message}')
                if 'gpt' in self.model_engine:
                    time.sleep(20)
                response_message = self.get_single_response(init_prompt)
            response_message = json.load(open(f'{self.output_dir}/{self.global_round}_response.json'))
        self.generator.format_ai_response(response_message)
        # process tasks
        self.process_tasks(response_message)
        self.generator.set_tasks(self.tasks)
        self.generator.add_history(None, self.global_round, self.update_data_lists)
        self.global_round += 1

        if self.execute == False:
            time.sleep(15)
        else:
            pass

    def run_code_generation_phase(self):
        # finish task one-by-one with code
        # print('[DEBUG] ', self.tasks)
        while len(self.tasks) > 0:
            task = self.tasks.pop(0)
            prompt = self.generator.get_prompt(
                data_list=self.update_data_lists,
                goal_description=task,
                global_round=self.global_round)
            self.generator.format_user_prompt(prompt=prompt, global_round=self.global_round)
            with Spinner(f'\033[32m[AI Thinking...]\033[0m'):
                response_message = self.get_single_response(prompt)
                while not self.valid_json_response(response_message):
                    print(f'\033[32m[Invalid Response, Waiting for 20s and Retrying...]\033[0m')
                    print(f'invalid response: {response_message}')
                    if 'gpt' in self.model_engine:
                        time.sleep(20)
                    response_message = self.get_single_response(prompt)
                response_message = json.load(open(f'{self.output_dir}/{self.global_round}_response.json'))
            self.generator.format_ai_response(response_message)

            # execute code
            with Spinner(f'\033[32m[AI Executing codes...]\033[0m'):
                print(f'\033[32m[Execute Code Start]\033[0m')
                execute_success, execute_info = self.execute_code(response_message)
                print('\033[32m[Execute Code Finish]\033[0m ', execute_success, execute_info)
                #TODO

            self.generator.add_history(task, self.global_round, self.update_data_lists, code=response_message['code'])
            self.global_round += 1
            if self.execute == False:
                time.sleep(15)

    def run(self):
        self.run_plan_phase()
        self.run_code_generation_phase()
        print(f'\033[31m[Job Finished! Cheers!]\033[0m')