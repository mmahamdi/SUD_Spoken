import difflib, glob, re
import pandas as pd
import numpy as np


############## Fonctions de correction ###################


def count_differences_punct(gold, eleve):
    diff = difflib.ndiff(gold, eleve)
    l=[d for d in diff]
    #print(l)
    erreurs=0
    for i in range(len(l)):
        d = l[i]
        #print(d[2])
        if d[2] =="…" and l[i+1][2] == ".":
            #print(d)
            erreurs=0
        elif d[0] != " ":
            erreurs+=1
    return erreurs

def count_differences_spelling(gold, eleve):
    
    diff = difflib.ndiff(gold, eleve)
    erreurs=0
    for d in diff:
        #print(d)
        if d[0] == "-":
            erreurs +=1
    return erreurs

def check_spelling(gold, eleve):

    #nettoyer
    gold = re.sub(r"(\.|,|\[|\]|\?|!|\"|:|\"|'|\(|\)|…)", "", gold)
    gold=gold.strip()
    gold = gold.replace(" ", "_")
    #print(gold)
    eleve = re.sub(r"(\.|,|\[|\]|\?|!|\"|:|\"|'|\(|\)|…)", "", eleve)
    eleve=eleve.strip()
    eleve = eleve.replace(" ", "_")
    gold=re.sub(r"__*","_", gold)
    eleve=re.sub(r"__*","_", eleve)
    gold = gold.split("_")
    eleve = eleve.split("_")
    #print(gold)
    #print(eleve)
    return str(count_differences_spelling(gold, eleve))

def check_punct(gold, eleve):
    
    import re
    gold = re.sub(r"\w'?|", "-", gold).replace(" ", "")
    eleve = re.sub(r"\w'?", "-", eleve).replace(" ", "")
    
    gold = gold.replace(".-.-.", "…")
    eleve = eleve.replace(".-.-.", "…")
    #print(gold, eleve)
    gold_maj = re.findall(r"\[|\]|\?|!|\.|\"|:|…", gold)
    eleve_maj = re.findall(r"\[|\]|\?|!|\.|\"|:|…", eleve)
    c=0
    gold_virg = re.findall(r',', gold)
    eleve_virg = re.findall(r',', eleve)
    
    # ponctuation majeure
    # si les gold_maj et eleve_maj ont des tailles différentes, on compte les différences jusqu'à la fin de gold_maj, puis on ajoute la somme d'éléments restants de eleve_maj
    # parce que je pars du principe que tout ce qui dépasse ou gold_maj ou est omis par rapport à gold_maj est à comptabiliser comme une erreur. 
    
    if len(gold_maj) > len(eleve_maj):
        #print(gold_maj, eleve_maj)
        c += count_differences_punct(gold_maj[:len(eleve_maj)], eleve_maj)
        c+=len(gold_maj[len(eleve_maj)::]) 
        
    elif len(gold_maj) < len(eleve_maj):
        #print(gold_maj, eleve_maj)
        c += count_differences_punct(gold_maj, eleve_maj[:len(gold_maj)])
        c+=len(eleve_maj[len(gold_maj)::])
        
    elif len(gold_maj) == len(eleve_maj):
        #print(gold_maj, eleve_maj)
        c+=count_differences_punct(gold_maj, eleve_maj)
        
    # virgules 
    
    if len(gold_virg)> len(eleve_virg) :
        c+= len(gold_virg)- len(eleve_virg)
        #print(gold_virg, eleve_virg)
    return str(c)


############### manipulation de fichier ####################


# traitement d'un seul tsv.
df = pd.read_csv("PS_2022_7_chienGourmand.tsv", sep='["]*\t', encoding="utf-8", engine='python')
for k, v in df.items():
    if k not in ["skahane","original", "menel.mahamdi", "kimgerdes", "kirianguiller", "kim.gerdes"]: # correcteurs+admins+original
        df_student = df[["skahane", k, "original"]]
        orth_student = []
        punct_student = []
        orth_original = []
        punct_original = []
        for index, row in df_student.iterrows():
            gold = row['skahane']
            stu = row[k]
            orig = row['original']
            
            orth_student.append(int(check_spelling(gold, stu)))
            punct_student.append(int(check_punct(gold, stu)))
            orth_original.append(int(check_spelling(gold, orig)))
            punct_original.append(int(check_punct(gold, orig)))  
            
            
        # colonnes valeurs
        df_student['ORTH_STUDENT'] = orth_student
        df_student['PUNCT_STUDENT'] = punct_student
        df_student['ORTH_ORIGINAL'] = orth_original
        df_student['PUNCT_ORIGINAL'] = punct_original
        df_student.loc['total'] = df_student.select_dtypes(np.number).sum()
        
        df_student.to_csv("PS_2022_7_"+k+".tsv", sep="\t")
