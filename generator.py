# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 15:25:36 2023

@author: cyshi
"""

import subprocess
from string import Template
import pandas as pd
import numpy as np

# Function to generate a certificate
def newcertificate(student, award, country, rank):
    # Open preexisting template
    # It has placeholders $student, $award, $country
    with open('template.tex', 'r') as template:
        text = Template(template.read())
    
    # Set filename after removing spaces from the country name
    # (pdflatex does not like spaces in filenames)
    filename = f'output/{country.replace(" ", "")}{rank}.tex'

    # Create a new file (for some reason, the default encoding was wrong)
    final = open(filename, 'w', encoding="utf-8")
    # Perform template substitution; this is just a string manipulation
    page = text.substitute(student = student, 
                           award = award,
                           country = country)
    # Actually write the nex text into the file
    final.write(page)

    # Close files, since we do not need them anymore
    template.close()
    final.close()
    
    # Call pdflatex. For some reason the background positioning requires two passes
    subprocess.call(f'pdflatex -output-directory output {filename}', stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    subprocess.call(f'pdflatex -output-directory output {filename}', stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

# Open the results
year = 2023
# why?
# This is in the Brazilian standard of using semicolons to separate columns
# Should be fixed for other applications
# REQUIRED preprocessing: convert to UTF-8 by opening the CSV in Notepad++
folder = "C:/Users/cyshi/OneDrive/Documentos/Matemática/Competições e Provas/APMO/2023/CertificatesV2/"
st=pd.read_csv(f"{folder}scoretable-{year}.csv", sep=";")

# Print number of countries and contestants
num_contestants=st.shape[0]
num_countries=len(st['country'].unique())
print(num_countries, num_contestants)

# Compute mean and (population) standard deviation
meanAPMO = np.mean(st.total)
stdAPMO = np.std(st.total)

# Compute cutoffs
gold = meanAPMO + stdAPMO
silver = meanAPMO + stdAPMO/3
bronze = meanAPMO - stdAPMO/3

# Compute awards
# Input: five APMO scores and rank in the country, in this order
def award(result):
    scores, rank = result[0:5],result[5]
    total = sum(scores)
    if total >= gold and rank <= 1:
        return('Gold Award')
    elif total >= silver and rank <=3:
        return('Silver Award')
    elif total >= bronze and rank <=7:
        return('Bronze Award')
    elif max(scores)==7:
        return 'Honorable Mention'
    else:
        return f'Rank {int(rank)}'

# Read problem scores and rank, and then compute award
prob_cols = [f'p{j}' for j in range(1,6)]
st['award'] = st[prob_cols+['rank']].apply(award, axis='columns')

# Generate certificate for each contestant
# It still generates certificates for students that did not get an award
for i in range(num_contestants):
    # The script takes a while to run, so it's good to keep tabs
    print(f"Generating certificate {i+1} of {num_contestants}...")
    # Concatenate first and last names
    name = f"{st['first'][i]} {st['last'][i]}"
    # Use attribute title() to fix ALL CAPS names
    newcertificate(name.title(), st['award'][i], st['country'][i], st['rank'][i])