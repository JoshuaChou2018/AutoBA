
## Introduction

**Automated Bioinformatics Analysis via AutoBA.** 

King Abdullah University of Science and Technology, KAUST

<a href='media/AutoBA_v2.pdf'><img src='https://img.shields.io/badge/Paper-PDF-red'></a>

https://github.com/JoshuaChou2018/AutoBA/assets/25849209/641309a7-3659-4e46-a599-2fc1b26db98f

```shell
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
```
## News

We are pleased to announce the official release of AutoBA's latest version `v0.0.1`! 🎉🎉🎉

The `main` branch serves as the primary branch, while the development branch is `dev`. 
Thank you for your unwavering support and enthusiasm, and let's work together to make AutoBA even more 
robust and powerful! If you want to contribute, please PR to `dev`. 💪

## Installation

```shell
conda create -n abc python==3.10
conda activate abc
conda install -c anaconda softwares -y
pip install openai==0.27.6 pyyaml
```

## Get Started

### Understand files

`./example` contains several examples for you to start.

Under `./example`, `config.yaml` defines your files and goals. Defining `data_list`, `output_dir` and `goal_description`
in `config.yaml` is mandatory before running `app.py`.

`app.py` run this file to start.

### Start with one command

Run this command to start a simple example.

`python app.py --config ./examples/case1.1/config.yaml --openai YOUR_OPENAI_API`

**Please note that this work uses the GPT-4 API and does not guarantee that GPT-3 will work properly in all cases.**

## Examples 

### Example 1: Bulk RNA-Seq

#### Case 1.1: Find differentially expressed genes

**Reference**: https://pzweuj.github.io/worstpractice/site/C02_RNA-seq/01.prepare_data/

Design of `config.yaml`
```yaml
data_list: [ './examples/case1.1/data/SRR1374921.fastq.gz: single-end mouse rna-seq reads, replicate 1 in LoGlu group',
            './examples/case1.1/data/SRR1374922.fastq.gz: single-end mouse rna-seq reads, replicate 2 in LoGlu group',
            './examples/case1.1/data/SRR1374923.fastq.gz: single-end mouse rna-seq reads, replicate 1 in HiGlu group',
            './examples/case1.1/data/SRR1374924.fastq.gz: single-end mouse rna-seq reads, replicate 2 in HiGlu group',
            './examples/case1.1/data/TruSeq3-SE.fa: trimming adapter',
            './examples/case1.1/data/mm39.fa: mouse mm39 genome fasta',
            './examples/case1.1/data/mm39.ncbiRefSeq.gtf: mouse mm39 genome annotation' ]
output_dir: './examples/case1.1/output'
goal_description: 'find the differentially expressed genes'
meta:
    info: 'meta-data recorded by users for reference only'
    title: 'The transcriptional landscape of mouse beta cells compared to human beta cells reveals notable species differences in long non-coding RNA and protein-coding gene expression, '
    url: 'https://pubmed.ncbi.nlm.nih.gov/25051960/'
```

##### Download Data
```shell
wget -P data/ http://hgdownload.soe.ucsc.edu/goldenPath/mm39/bigZips/genes/mm39.ncbiRefSeq.gtf.gz
wget -P data/ http://hgdownload.soe.ucsc.edu/goldenPath/mm39/bigZips/mm39.fa.gz
gunzip data/mm39.ncbiRefSeq.gtf.gz
gunzip data/mm39.fa.gz
wget -P data/ ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR137/001/SRR1374921/SRR1374921.fastq.gz
wget -P data/ ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR137/002/SRR1374922/SRR1374922.fastq.gz
wget -P data/ ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR137/003/SRR1374923/SRR1374923.fastq.gz
wget -P data/ ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR137/004/SRR1374924/SRR1374924.fastq.gz
```

```shell
python app.py --config ./examples/case1.1/config.yaml
```

#### Case 1.2: Identify top5 down-regulated genes in HiGlu group

**Reference**: https://pzweuj.github.io/worstpractice/site/C02_RNA-seq/01.prepare_data/

Design of `config.yaml`
```yaml
data_list: [ './examples/case1.2/data/SRR1374921.fastq.gz: single-end mouse rna-seq reads, replicate 1 in LoGlu group',
            './examples/case1.2/data/SRR1374922.fastq.gz: single-end mouse rna-seq reads, replicate 2 in LoGlu group',
            './examples/case1.2/data/SRR1374923.fastq.gz: single-end mouse rna-seq reads, replicate 1 in HiGlu group',
            './examples/case1.2/data/SRR1374924.fastq.gz: single-end mouse rna-seq reads, replicate 2 in HiGlu group',
            './examples/case1.2/data/TruSeq3-SE.fa: trimming adapter',
            './examples/case1.2/data/mm39.fa: mouse mm39 genome fasta',
            './examples/case1.2/data/mm39.ncbiRefSeq.gtf: mouse mm39 genome annotation' ]
output_dir: './examples/case1.2/output'
goal_description: 'Identify top5 down-regulated genes in HiGlu group'
meta:
    info: 'meta-data recorded by users for reference only'
    title: 'The transcriptional landscape of mouse beta cells compared to human beta cells reveals notable species differences in long non-coding RNA and protein-coding gene expression, '
    url: 'https://pubmed.ncbi.nlm.nih.gov/25051960/'
```

##### Download Data
```shell
wget -P data/ http://hgdownload.soe.ucsc.edu/goldenPath/mm39/bigZips/genes/mm39.ncbiRefSeq.gtf.gz
wget -P data/ http://hgdownload.soe.ucsc.edu/goldenPath/mm39/bigZips/mm39.fa.gz
gunzip data/mm39.ncbiRefSeq.gtf.gz
gunzip data/mm39.fa.gz
wget -P data/ ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR137/001/SRR1374921/SRR1374921.fastq.gz
wget -P data/ ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR137/002/SRR1374922/SRR1374922.fastq.gz
wget -P data/ ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR137/003/SRR1374923/SRR1374923.fastq.gz
wget -P data/ ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR137/004/SRR1374924/SRR1374924.fastq.gz
```

```shell
python app.py --config ./examples/case1.2/config.yaml
```

#### Case 1.3: Predict Fusion genes using STAR-Fusion

**Reference:** https://github.com/STAR-Fusion/STAR-Fusion-Tutorial/wiki

Design of `config.yaml`
```yaml
data_list: [ './examples/case1.3/data/rnaseq_1.fastq.gz: RNA-Seq read 1 data (left read)',
            './examples/case1.3/data/rnaseq_2.fastq.gz: RNA-Seq read 2 data (right read)',
            './examples/case1.3/data/CTAT_HumanFusionLib.mini.dat.gz: a small fusion annotation library',
            './examples/case1.3/data/minigenome.fa: small genome sequence consisting of ~750 genes.',
            './examples/case1.3/data/minigenome.gtf: transcript structure annotations for these genes' ]
output_dir: './examples/case1.3/output'
goal_description: 'Predict Fusion genes using STAR-Fusion'
```

##### Download Data

```shell
cd data
git clone https://github.com/STAR-Fusion/STAR-Fusion-Tutorial.git
mv STAR-Fusion-Tutorial/* .
```

### Example 2: Single Cell RNA-seq Analysis

#### Case 2.1: Find the differentially expressed genes

**Reference:** https://www.jianshu.com/p/e22a947e6c60

Design of `config.yaml`
```yaml
data_list: [ './examples/case2.1/data/filtered_gene_bc_matrices/hg19: path to 10x mtx data',]
output_dir: './examples/case2.1/output'
goal_description: 'use scanpy to find the differentially expressed genes'
```

##### Download Data

```shell
wget -P data/ http://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz
cd data
tar zxvf pbmc3k_filtered_gene_bc_matrices.tar.gz
```

#### Case 2.2: Perform clustering

**Reference:** https://www.jianshu.com/p/e22a947e6c60

Design of `config.yaml`
```yaml
data_list: [ './examples/case2.2/data/filtered_gene_bc_matrices/hg19: path to 10x mtx data',]
output_dir: './examples/case2.2/output'
goal_description: 'use scanpy to perform clustering and visualize the expression level of gene PPBP in the UMAP.'
```

#### Case 2.3: Identify top5 marker genes

**Reference:** https://www.jianshu.com/p/e22a947e6c60

Design of `config.yaml`
```yaml
data_list: [ './examples/case2.3/data/filtered_gene_bc_matrices/hg19: path to 10x mtx data',]
output_dir: './examples/case2.3/output'
goal_description: 'use scanpy to identify top5 marker genes'
```

### Example 3: ChIP-Seq Analysis

#### Case 3.1: Call peaks

**Reference:** https://pzweuj.github.io/2018/08/22/chip-seq-workflow.html

Design of `config.yaml`


##### Download Data

```shell
# 下载了5个样本，分别是Ring1B、cbx7、SUZ12、RYBP、IgGold。
for ((i=204; i<=208; i++)); \
do wget ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR620/SRR620$i/SRR620$i.fastq.gz; \
done

wget http://hgdownload.soe.ucsc.edu/goldenPath/mm39/bigZips/genes/mm39.ncbiRefSeq.gtf.gz
wget http://hgdownload.soe.ucsc.edu/goldenPath/mm39/bigZips/mm39.fa.gz
gunzip mm39.ncbiRefSeq.gtf.gz
gunzip mm39.fa.gz
```

Design of `config.yaml`
```yaml
data_list: [ './examples/case3.1/data/SRR620204.fastq.gz: chip-seq data for Ring1B',
            './examples/case3.1/data/SRR620205.fastq.gz: chip-seq data for cbx7',
            './examples/case3.1/data/SRR620206.fastq.gz: chip-seq data for SUZ12',
            './examples/case3.1/data/SRR620208.fastq.gz: chip-seq data for IgGold',
            './examples/case3.1/data/mm39.ncbiRefSeq.gtf: genome annotations mouse',
            './examples/case3.1/data/mm39.fa: mouse genome' ]
output_dir: './examples/case3.1/output'
goal_description: 'call peaks for protein cbx7 with IgGold as control'
```

#### Case 3.2: Discover motifs within the peaks

Design of `config.yaml`
```yaml
data_list: [ './examples/case3.2/data/SRR620204.fastq.gz: chip-seq data for Ring1B',
            './examples/case3.2/data/SRR620205.fastq.gz: chip-seq data for cbx7',
            './examples/case3.2/data/SRR620206.fastq.gz: chip-seq data for SUZ12',
            './examples/case3.2/data/SRR620208.fastq.gz: chip-seq data for IgGold',
            './examples/case3.2/data/mm39.ncbiRefSeq.gtf: genome annotations mouse',
            './examples/case3.2/data/mm39.fa: mouse genome' ]
output_dir: './examples/case3.2/output'
goal_description: 'Discover motifs within the peaks of protein SUZ12 with IgGold as control'
```

#### Case 3.3: Functional Enrichment
Design of `config.yaml`
```yaml
data_list: [ './examples/case3.3/data/SRR620204.fastq.gz: chip-seq data for Ring1B',
            './examples/case3.3/data/SRR620205.fastq.gz: chip-seq data for cbx7',
            './examples/case3.3/data/SRR620206.fastq.gz: chip-seq data for SUZ12',
            './examples/case3.3/data/SRR620208.fastq.gz: chip-seq data for IgGold',
            './examples/case3.3/data/mm39.ncbiRefSeq.gtf: genome annotations mouse',
            './examples/case3.3/data/mm39.fa: mouse genome' ]
output_dir: './examples/case3.3/output'
goal_description: 'perform functional enrichment for protein Ring1B, use protein IgGold as the control'
```

### Example 4: Spatial Transcriptomics

#### Case 4.1: Neighborhood enrichment analysis

**Reference:** https://squidpy.readthedocs.io/en/latest/notebooks/tutorials/tutorial_seqfish.html

Design of `config.yaml`
```yaml
data_list: [ './examples/case4.1/data/slice1.h5ad: spatial transcriptomics data for slice 1 in AnnData format',]
output_dir: './examples/case4.1/output'
goal_description: 'use squidpy for neighborhood enrichment analysis'
```

## More Examples for Developer

To use AutoBA in your case, please copy `config.yaml` to your destination and modify it accordingly.
Then you are ready to go. We welcome all developers to submit PR to upload your special cases under `./projects`

## Citation
If you find this project useful in your research, please consider citing:

```bibtex
@misc{zhou2023,
    title={Automated Bioinformatics Analysis via AutoBA},
    author={Juexiao Zhou},
    howpublished = {\url{https://github.com/JoshuaChou2018/AutoBA}},
    year={2023}
}
```
