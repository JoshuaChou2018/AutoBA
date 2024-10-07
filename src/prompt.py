#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：Auto-BioinfoGPT 
@File    ：prompt.py
@Author  ：Juexiao Zhou
@Contact : juexiao.zhou@gmail.com
@Date    ：2023/5/2 11:07 
'''
from copy import deepcopy
from src.build_RAG_private import retrive
import time

class PromptGenerator:
    def __init__(self, blacklist='', engine = None, rag = False, retriever = None):
        self.history_summary = ''
        self.current_goal = None
        self.global_goal = None
        self.tasks = None
        self.engine = engine
        self.rag = rag
        self.retriever = retriever
        self.blacklist = blacklist.split(',')
        self.speciallist = ['sra-toolkit: micromamba install sra-tools',
                            'trim_galore: micromamba install trim-galore']

    def get_executor_prompt(self, executor_info):
        prompt = {
            "task": "I executed a Bash script and obtained log output detailing its execution. Kindly assist me in assessing the success of the script. If it encounters any failures, please aid in summarizing the reasons for the failure and propose modifications to the code.",
            "rules": [
                "You should only respond in JSON format with fixed format.",
                "Your JSON response should only be enclosed in double quotes.",
                "No such file or directory is error."
                "You should not write anything outside {}.",
                "You should make your answer as detailed as possible.",
            ],
            "log output": [
                executor_info
            ],
            "fixed format": {
                "stat": "0 or 1, 0 indicates failure and 1 indicates success",
                "info": "summarize errors in one sentence."
            }
        }
        final_prompt = prompt
        return final_prompt

    def get_prompt(self, data_list, goal_description, global_round, execute_success=True, execute_info=None, last_execute_code=None):
        """

        :param data_list: ['data path: data description']
        :param goal_description: 'goal'
        :param global_round: int
        :return:
        """
        self.current_goal = goal_description
        if global_round == 0:
            self.global_goal = goal_description
            prompt = {
                    "role": "Act as a bioinformatician, the rules must be strictly followed!",
                    "rules": [
                        "When acting as a bioinformatician, you strictly cannot stop acting as a bioinformatician.",
                        "All rules must be followed strictly.",
                        "You should use information in input to write a detailed plan to finish your goal.",
                        f"You should include the software name and should not use those software: {self.blacklist}.",
                        "You should only respond in JSON format with my fixed format.",
                        "Your JSON response should only be enclosed in double quotes and you can have only one JSON in your response.",
                        "You should not write loading data as a separate step.",
                        "You should not write anything else except for your JSON response.",
                        "You should make your answer as detailed as possible."
                    ],
                    "input": [
                            "You have the following information in a list with the format file path: file description. I provide those files to you, so you don't need to prepare the data.",
                            data_list
                        ],
                    "goal": self.current_goal,
                    "fixed format for JSON response": {
                        "plan": [
                            "Your detailed step-by-step sub-tasks in a list to finish your goal in the format: use some tool to do some task."
                        ]
                    }
                }
            final_prompt = prompt
        else:
            if self.rag:
                retriever_info = retrive(self.retriever,
                                         retriever_prompt=f'{self.current_goal}')
            else:
                retriever_info = ''
            prompt = {
                "role": "Act as a bioinformatician, the rules must be strictly followed!",
                "rules": [
                    "When acting as a bioinformatician, you strictly cannot stop acting as a bioinformatician.",
                    "All rules must be followed strictly.",
                    "You are provided a system with specified constraints."
                    "The history of what you have done is provided, you should take the name changes of some files into account, or use some output from previous steps.",
                    "You should use all information you have to write bash codes to finish your current task.",
                    "All code requirements must be followed strictly when you write codes.",
                    "You should only respond in JSON format with my fixed format.",
                    "Your JSON response should only be enclosed in double quotes.",
                    "You should make your answer as simple as possible.",
                    "You should not write anything else except for your JSON response.",
                    'You should use full absolute path for all files.',
                ],
                "system": [
                    "You have a Ubuntu 24.04 system",
                    "You have a micromamba environment named abc_runtime",
                    "You do not have any other software installed"
                ],
                "input": [
                        "You have the following information in a list with the format file path: file description. I provide those files to you, so you don't need to prepare the data.",
                        data_list
                    ],
                "history": self.history_summary,
                "current task": self.current_goal,
                "code requirement": [
                    f"You should not use those software: {self.blacklist}.",
                    "You should not create and activate the micromamba environment abc_runtime.",
                    'You should install dependencies and software you need to use with micromamba or pip with -y.',
                    'You should pay attention to the number of input files and do not miss any.',
                    'You should process each file independently and can not use FOR loop.',
                    'You should use the default values for all parameters that are not specified.',
                    'You should not repeat what you have done in history.',
                    'You should only use software directly you installed with micromamba or pip.',
                    'If you use Rscript -e, you should make sure all variables exist in your command, otherwise, you need to check your history to repeat previous steps and generate those variables.',
                    "You should not write anything else except for your JSON response.",
                    "If RAG is provided, you should use it as template to write codes. You should not copy the RAG directly."
                ],
                "RAG: If provided, you should replace <...> with correct values and file paths based on information in history": retriever_info,
                "fixed format for JSON response": {
                    "tool": "name of the tool you use",
                    "code": "bash code to finish the current task in one line."
                }
            }
            if execute_success:
                final_prompt = prompt
            else:
                final_prompt = prompt
                final_prompt['history'] += f' You previously generated codes: {last_execute_code}. However, your code has errors and you should fix them: {execute_info}.'
                #final_prompt['code requirement'].append(f' You previously generated codes: {last_execute_code}. However, your code has errors and you should fix them: {execute_info}. You should use those software in correct way: {self.speciallist}')

        return final_prompt

    def set_tasks(self, tasks):
        self.tasks = deepcopy(tasks)

    def slow_print(self, input_string, speed=0.01):
        for char in str(input_string):
            # 使用print函数打印每个字符，并设置end参数为空字符串，以避免在每个字符之间输出换行符
            try:
                print(char, end='', flush=True)
            except:
                print(char, end='')
            time.sleep(speed)
        print()

    def format_user_prompt(self, prompt, global_round, gui_mode):
        INFO_STR = ''
        if gui_mode:
            print(f'[Round {global_round}]')
            print(f'[USER]')
            INFO_STR += f'[Round {global_round}] \n\n'
            for key in prompt:
                self.slow_print(f"{key}", speed=0.001)
                self.slow_print(prompt[key], speed=0.001)
                INFO_STR += f"{key} \n\n {prompt[key]} \n\n"
        else:
            print(f'\033[31m[Round {global_round}]\033[0m')
            print(f'\033[32m[USER]\033[0m')
            INFO_STR += f'\033[31m[Round {global_round}]\033[0m \n\n'
            for key in prompt:
                self.slow_print(f"\033[34m{key}\033[0m", speed=0.001)
                self.slow_print(prompt[key], speed=0.001)
                INFO_STR += f"\033[34m{key}\033[0m \n\n {prompt[key]} \n\n"
        print()
        return INFO_STR

    def format_ai_response(self, response_message, gui_mode):
        INFO_STR = ''
        if gui_mode:
            print(f'[AI]')
            for key in response_message:
                self.slow_print(f"{key}", speed=0.01)
                self.slow_print(response_message[key], speed=0.01)
                INFO_STR += f"{key} \n\n {response_message[key]} \n\n"
            print(f'-------------------------------------')
        else:
            print(f'\033[32m[AI]\033[0m')
            for key in response_message:
                self.slow_print(f"\033[34m{key}\033[0m", speed=0.01)
                self.slow_print(response_message[key], speed=0.01)
                INFO_STR += f"\033[34m{key}\033[0m \n\n {response_message[key]} \n\n"
            print(f'\033[33m-------------------------------------\033[0m')
        print()
        return INFO_STR

    def add_history(self, task, global_round, data_list, code = None):
        if global_round == 0:
            self.history_summary += f"Firstly, you have input with the format 'file path: file description' in a list: {data_list}. You wrote a detailed plan to finish your goal. Your global goal is {self.global_goal}. Your plan is {self.tasks}. \n"
        else:
            self.history_summary += f"Then, you finished the task: {task} with code: {code}.\n"