from DNAContamination import DNAContamination

def test(s,k,l):
    file = open('target_batch.fasta', 'r')

    if file is None:
        raise ValueError("file not found")

    index_c = 1
    all_contaminants = {}
    max_contaminants = []

    Contaminants = DNAContamination(s, l)


    while True:
        line = file.readline()
        if not line:
            break
        if '>' not in line:
            contam = line[:len(line)]
            all_contaminants[contam] =  index_c
            #print("Cont "+ str(index_c) + " ")
            Contaminants.addContaminants(contam)
            index_c = index_c + 1

    k_contaminants = Contaminants.getContaminants(k)


    for i in range(len(k_contaminants)):
        max_contaminants.append(all_contaminants[k_contaminants[i]])

    max_contaminants.sort()

    output_str = ""
    for i in range(len(max_contaminants)):
        if i == 0:
            output_str = output_str + str(max_contaminants[i])+","
        elif i == len(max_contaminants) - 1:
            output_str = output_str + " " + str(max_contaminants[i])
        else:
            output_str = output_str + " " + str(max_contaminants[i]) + ","

    return output_str


dna = 'CGCTGTACATGATGAAATGGGAGGTGCTTCTATTGACATACCTCGACCGACCCCGTTTCCTGTGCGCAGAATACCTTGGCTCGTATTAGGTGAGCAGCCAAGGCGTGTCACAAGAGGGGTTGATCCGGGTTTCGGGCGATTCTCGAACCACCACTAGCGACATGCCGGCTTGGTCTGGCGTCGGCCTATATTACGCTCCCCCAATAATATCAATCTACCAGCTCCCGTTTAAGTTCTAGTATGTAAGCGGACTCGTAGGGTACAACCTTCTTTATG'
k = 15
l = 8
print(test(dna, k, l))