# -*- coding: utf-8 -*-
"""
@Time ： 2024/1/15 11:45
@Auth ： Juexiao Zhou
@File ：app.py
@IDE ：PyCharm
@Page: www.joshuachou.ink
"""

import argparse
import os
from src.agent import Agent
import gradio as gr
import time
import yaml
import subprocess
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="AutoBA-GUI v0.1")
    parser.add_argument('--port', type=int, default=5904)
    args = parser.parse_args()
    return args

def gradio_reset():
    return None, None, None

def get_an_example():
    _input_file_path_description = "./experiments/case1.1/data/SRR1234567_R1.fastq.gz: Paired-end Illumina WGS reads, forward\n" \
                                   "./experiments/case1.1/data/SRR1234567_R2.fastq.gz: Paired-end Illumina WGS reads, reverse\n" \
                                   "./experiments/case1.1/data/TruSeq3-PE.fa: Adapter sequences for trimming\n" \
                                   "./experiments/case1.1/data/Reference.fasta: Reference genome for the organism under study in FASTA format"
    _input_outoput_path = "./experiments/case1.1/output"
    _input_goal = "To perform genome assembly using paired-end WGS data"
    return _input_file_path_description, _input_outoput_path, _input_goal

def print_to_textbox(*args, **kwargs):
    global HISTORY
    text = " ".join(map(str, args)) + "\n"
    if len(HISTORY) > 100:
        HISTORY = HISTORY[1:]
        HISTORY.append(text)
    else:
        HISTORY.append(text)

def run(input_file_path_description, input_outoput_path, input_goal, model_engine, openai_api, execute):
    AIAgent = Agent(initial_data_list=input_file_path_description.split('\n'),
                    output_dir=input_outoput_path,
                    initial_goal_description=input_goal,
                    model_engine=model_engine,
                    openai_api=openai_api,
                    execute=execute,
                    blacklist='STAR,java,perl,annovar',
                    gui_mode=False)
    AIAgent.run()
    return 'Job Finished!'


if __name__ == '__main__':
    args = parse_args()
    # model_folder = args.model_root
    # model_files = [os.path.join(model_folder, f) for f in os.listdir(model_folder) if os.path.isfile(os.path.join(model_folder, f))]
    FORCE_STOP = False
    HISTORY = []

    with gr.Blocks() as demo:
        gr.Markdown("""<h1 align="center">AutoBA-GUI v0.1</h1>""")

        gr.Markdown("""<h3>An AI Agent for Fully Automated Multi-omic Analyses</h3>""")

        with gr.Row():
            with gr.Column():
                input_file_path_description = gr.TextArea(
                    label="File path and description",
                    placeholder="Enter the absolute file path and file description in the following format, e.g.: \n"
                                "/data/SRR1234567_R1.fastq.gz: Paired-end Illumina WGS reads, forward\n"
                                "/data/SRR1234567_R2.fastq.gz: Paired-end Illumina WGS reads, reverse\n"
                                "/data/TruSeq3-PE.fa: Adapter sequences for trimming\n"
                                "/data/Reference.fasta: Reference genome for the organism under study in FASTA format",
                    max_lines=999999,
                    container=True,
                )

                input_outoput_path = gr.TextArea(
                    label="Output path",
                    placeholder="Enter absolute output path, e.g.: \n"
                                "/output",
                    max_lines=999999,
                    container=True,
                )

                input_goal = gr.TextArea(
                    label="Goal",
                    placeholder="Describe your goal for analysis, e.g.: \n"
                                "To perform genome assembly using paired-end WGS data",
                    max_lines=999999,
                    container=True,
                )

                local_model_engines = ['codellama-7bi',
                                       'codellama-13bi',
                                       'codellama-34bi',
                                       'llama2-7bc',
                                       'llama2-13bc',
                                       'llama2-70bc']

                gpt_model_engines = ['gpt-3.5-turbo',
                                     'gpt-4',
                                     'gpt-3.5-turbo-1106',
                                     'gpt-4-0613',
                                     'gpt-4-32k-0613',
                                     'gpt-4-1106-preview']

                model_engines = local_model_engines + gpt_model_engines

                with gr.Row():
                    model_engine = gr.Dropdown(
                        label="Select model engine",
                        choices=model_engines,
                        value='gpt-4-1106-preview',
                        max_choices=1,
                        container=True,
                        interactive=True
                    )

                    openai_api = gr.Textbox(
                        label="OpenAI API",
                        placeholder="sk-xxxxx. Leave it empty for local version ",
                        max_lines=1,
                        container=True,
                        interactive=True
                    )

                    execute = gr.Checkbox(
                        label="Execute Code",
                        value=False,
                        visible=True
                    )

                with gr.Row():
                    example_button = gr.Button(
                        value="Get an example",
                        interactive=True,
                        variant="primary"
                    )

                    upload_button = gr.Button(
                        value="Run",
                        interactive=True,
                        variant="primary"
                    )

                    #clear = gr.Button("Restart")

                with gr.Row():
                    with gr.Column():
                        gr.Markdown('### Check command line for realtime outputs')
                        output_log = gr.TextArea(
                            label="Check command line for realtime outputs",
                            max_lines=5,
                            container=True,
                            lines=5,
                        )

        gr.Markdown("""This site was created by King Abdullah University of Science and Technology (KAUST).""")

        click_event = upload_button.click(run,
                            [input_file_path_description, input_outoput_path, input_goal, model_engine, openai_api,
                             execute],
                            [output_log])

        example_button.click(get_an_example,
                             [],
                             [input_file_path_description, input_outoput_path, input_goal])

    demo.launch(share=True, server_port=args.port, server_name='0.0.0.0')
