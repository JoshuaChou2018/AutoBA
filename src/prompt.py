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
import time

class PromptGenerator:
    def __init__(self):
        self.history_summary = ''
        self.current_goal = None
        self.global_goal = None
        self.tasks = None
        self.blacklist = ['STAR', 'java']
        self.special_softwares = ['hisat2, HISAT2, bowtie2: you should build genome index as the first step, use -U if input files are single-end reads, use -1 and -2 if input files are paird-end reads, you should use --readFilesCommand zcat if your input files ends with .gz, you should process each .gz separately. ',
                                  'trimmomatic: you should substitute with cutadapter. ',
                                  'cutadapter: you should name files with the id as prefix. '
                                  'featureCounts: you should use cut to extract the first column and the columns >=7 into a new file at the final step. '
                                  "DESeq2: you should install BiocManager with repos='http://cran.us.r-project.org' ",
                                  "macs2: you should use -g hs for human and -g mm for mouse. ",
                                  "gsea: you should substitute gsea-cli.sh with gsea-cli, you should use -set_max, -set_min and -zip_report false"
                                ]

    def get_prompt(self, data_list, goal_description, global_round):
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
                    "You should only respond in JSON with the required format.",
                    "Your JSON should only enclosed in double quotes."
                ],
                "input": [
                        "You have the following information in a list with the format file path: file description. I provide those files to you, so you don't need to prepare the data.",
                        data_list
                    ],
                "goal": self.current_goal,
                "format": {
                    "plan": [
                        "Your detailed step-by-step sub-tasks to finish your goal."
                    ]
                }
            }
            final_prompt = prompt
        else:
            prompt = {
                "role": "Act as a bioinformatician, the rules must be strictly followed!",
                "rules": [
                    "When acting as a bioinformatician, you strictly cannot stop acting as a bioinformatician.",
                    "All rules must be followed strictly.",
                    "You are provided a system with specified constraints."
                    "The history of what you have done is provided, you should take the name changes of some files into account, or use some output from previous steps.",
                    "You should use all information you have to write bash codes to finish your current task.",
                    "All code requirements must be followed strictly when you write codes.",
                    "You should only respond in JSON with the required format.",
                    "Your JSON should only enclosed in double quotes."
                ],
                "system": [
                    "You have a Ubuntu 18.04 system",
                    "You have a conda environment named abc",
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
                    'You should always source activate the environment abc first.',
                    'You should always install dependencies with -y with conda or pip.',
                    'You should pay attention to the number of input files and do not miss any.',
                    'You should process each file independently and can not use FOR loop.',
                    'You should use the path for all files according to input and history.',
                    'You should use the default values for all parameters that are not specified.',
                    'You should not repeat what you have done in history.',
                    'You should only use software directly you installed with conda.',
                ],
                "format": {
                    "tool": "name of the tool you use",
                    "code": "bash code to finish the current task"
                }
            }
            final_prompt = prompt

        return final_prompt

    def set_tasks(self, tasks):
        self.tasks = deepcopy(tasks)

    def slow_print(self, input_string, speed=0.01):
        for char in str(input_string):
            # 使用print函数打印每个字符，并设置end参数为空字符串，以避免在每个字符之间输出换行符
            print(char, end='', flush=True)
            time.sleep(speed)
        print()

    def format_user_prompt(self, prompt, global_round):
        print(f'\033[31m[Round {global_round}]\033[0m')
        print(f'\033[32m[USER]\033[0m')
        for key in prompt:
            self.slow_print(f"\033[34m{key}\033[0m", speed=0.001)
            self.slow_print(prompt[key], speed=0.001)
        print()

    def format_ai_response(self, response_message):
        print(f'\033[32m[AI]\033[0m')
        for key in response_message:
            self.slow_print(f"\033[34m{key}\033[0m", speed=0.01)
            self.slow_print(response_message[key], speed=0.01)
        print(f'\033[33m-------------------------------------\033[0m')
        print()

    def add_history(self, task, global_round, data_list, code = None):
        if global_round == 0:
            self.history_summary += f"Firstly, you have input with the format 'file path: file description' in a list: {data_list}. You wrote a detailed plan to finish your goal. Your global goal is {self.global_goal}. Your plan is {self.tasks}. \n"
        else:
            self.history_summary += f"Then, you finished the task: {task} with code: {code}.\n"