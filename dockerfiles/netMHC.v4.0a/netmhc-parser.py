import re
from Bio import SeqIO
import argparse
from itertools import compress
import subprocess
import sys
import os
from os.path import basename
import shutil

def process_hlaminer(input_file):
    alleles = []
    infile = open(input_file)
    for line in infile:
        line = line.strip()
        if 'Prediction' in line:
            allele_line = next(infile).strip()
            if allele_line:
                alleles.append(allele_line.split(',')[0])
    alleles_bool = map(lambda x: x if re.match(r'^[A|B|C].*', x) else False, alleles)
    return list(compress(alleles, alleles_bool))

def run_command(command, stdout=subprocess.PIPE):
    print command
    process = subprocess.Popen(command, shell=True, stdout=stdout)
    out, err = process.communicate()
    return out

def get_MHCalleles():
    command = '/opt/netMHC-4.0/Linux_x86_64/bin/netMHC -listMHC > alleles_db/listMHC.fasta'
    run_command(command, subprocess.PIPE)
    out = open('alleles_db/listMHC.fasta').read()
    mhc_alleles = filter(lambda x: x if not x.startswith('#') else False, out.split('\n'))
    return mhc_alleles

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '-hla', '--hla-input-file',
        help='HLAminer Input file')
    parser.add_argument(
        '-d', '--database-file',
        help='input IMGT database file')
    parser.add_argument(
        '-f', '--input-protein-file',
        help='input protein file')
    parser.add_argument(
        '-l', '--peptide-length', default=9, type=int,
        help='input peptide length')

    args = parser.parse_args()

    # set args
    peptide_length = args.peptide_length

    alelle_dir = 'alleles_db/'
    if os.path.exists(alelle_dir):
        shutil.rmtree(alelle_dir)
    os.mkdir(alelle_dir, 0777);
    out_dir = 'outputs/'
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.mkdir(out_dir, 0777);

    all_alleles = get_MHCalleles()
    output_prefix = os.path.splitext(basename(args.input_protein_file))[0]
    for allele in process_hlaminer(args.hla_input_file):
        allele_to_search = allele
        allele = re.sub('\*', '', allele)
        allele =  'HLA-' + re.sub('P$', '', allele)
        netMHC_outxls = output_prefix + '.' + allele.replace(":", "-", 1) + '.xls'
        allele_fasta = alelle_dir + re.sub('\*', '', allele) + '.fasta'
        netMHC_outtxt = output_prefix + '.' + allele.replace(":", "-", 1)  + '.txt'


        if allele in all_alleles:
            print allele
            run_command('/opt/netMHC-4.0/Linux_x86_64/bin/netMHC -l {4} -a {0} -f {1} -xls -xlsfile outputs/{2} > outputs/{3}'
                .format(allele, args.input_protein_file, netMHC_outxls, netMHC_outtxt, peptide_length))
            continue

