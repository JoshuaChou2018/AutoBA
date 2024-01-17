# -*- coding: utf-8 -*-
"""
@Time ： 2023/12/11 12:49
@Auth ： Juexiao Zhou
@File ：executor.py
@IDE ：PyCharm
@Page: www.joshuachou.ink
"""

import subprocess
import time

class CodeExecutor:
    def __init__(self):
        self.bash_code_path = None
        self.code_prefix = [
            'conda create -n abc_runtime python==3.10 -y',
            'source activate abc_runtime',
            'which python',
            'conda config --set show_channel_urls false',
            'conda config --add channels conda-forge',
            'conda config --add channels bioconda',
        ]
        self.code_postfix = [
        ]

    def execute(self, bash_code_path):

        self.bash_code_path = bash_code_path
        with open(self.bash_code_path, 'r') as input_file:
            bash_content = input_file.read()

        self.bash_code_path_execute = self.bash_code_path + '.execute.sh'

        # 打开新生成的 Bash 文件以供写入
        with open(self.bash_code_path_execute, 'w') as output_file:
            for code in self.code_prefix:
                output_file.write(code + '\n')
            # 写入原始内容
            output_file.write(bash_content)
            output_file.write('\n')  # 确保在新行开始
            for code in self.code_postfix:
                output_file.write(code + '\n')

        # 使用 subprocess 执行 Bash 文件，将输出捕获到一个字符串中
        process = subprocess.Popen(['bash', '-i', '-e', self.bash_code_path_execute],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            text=True)

        # 实时读取输出并打印
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            print(f'[stdout] {output.strip()}')

        stderr = []
        for _ in process.stderr.readlines():
            if 'EnvironmentNameNotFound' in _ or '\n' == _:
                pass
            else:
                print(f"[stderr] {_}", end='')
                stderr.append(_)

        if len(stderr) > 30:
            stderr = stderr[-30:]

        stderr = ''.join(stderr)
        process.communicate()

        executor_info = stderr
        return executor_info