#!/usr/bin/env python

import pysam
import pandas as pd


# possible filters
query_length=30
is_paired=True
is_duplicate=False
is_qcfail=False
is_secondary=False
is_supplementary=False
is_unmapped=False
mapping_quality=0
query_alignment_length=50
#np.mean(a.query_qualities[1])=30
#np.mean(a.query_alignment_qualities[1])=30


def filter_read(aln):
    if aln.query_length >= 30:
        return True
    else:
        return False
        

samfile = pysam.AlignmentFile("test.bam", "rb") 
df = pd.DataFrame(samfile.header['SQ'])
df['start'] = [0]*len(df.index)
df.columns = ['stop', 'contig', 'start']  

for i in df.index: 
    stop, contig, start = df.loc[i,] 
    count = samfile.count(contig=contig, start=start, stop=stop, region=None, until_eof=False, read_callback=filter_read)
    if count > 0:
        print(i, contig, count)





