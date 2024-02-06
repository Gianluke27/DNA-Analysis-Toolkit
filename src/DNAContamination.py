"""
You are required to identify the contaminants with higher degree of contamination in s.
Specifically, you must implement a class DNAContamination that allows to verify the
degree of contamination in a string s by a set of contaminants C. The class implements the
following methods:
● DNAContamination(s, l): it build a DNAContamination object; it takes in input the
string s to verify and the contamination threshold l (the contaminant set C is initially
empty);
● addContaminant(c): it adds contaminant c to the set C and saves the degree of
contamination of s by c;
● getContaminants(k): it returns the k contaminants with larger degree of
contamination among the added contaminants.
"""

from TdP_collections.priority_queue import heap_priority_queue
from SuffixTree import SuffixTree
from TdP_collections.queue.array_queue import ArrayQueue
from TdP_collections.tree import tree


class DNAContamination:

######### PRIVATE ###############
    class _Position(tree.Tree.Position):
        def __init__(self, container, node):
            self._container = container
            self._node = node

        def element(self):
            return str(self._node._firstmark) + "," + str(self._node._startIndex) + ":" + str(self._node._stopIndex) + "  all marks: " + str(self._node._mark.keys())

        def __eq__(self, other):
            return self == other

        def __ne__(self, other):
            return not (self == other)

    def _validate(self, p):
        """Return associated node, if position is valid."""
        if not isinstance(p, self._Position):
            raise TypeError('p must be proper Position type')
        if p._container is not self:
            raise ValueError('p does not belong to this container')
        if p._node._parent is p._node:  # convention for deprecated nodes
            raise ValueError('p is no longer valid')
        return p._node

    def _make_position(self, node):
        """Return Position instance for given node (or None if no node)."""
        return self._Position(self, node) if node is not None else None

    def _children(self, p):
        """Generate an iteration of Positions representing p's children."""
        node = self._validate(p)
        for child in node._children.values():
            yield self._make_position(child)

    def _breadthfirst(self,tree):
        """Generate a breadth-first iteration of the positions of the alberi."""
        if not tree.is_empty():
            fringe = ArrayQueue()  # known positions not yet yielded
            fringe.enqueue(self._make_position(tree.root))  # starting with the root
            while not fringe.is_empty():
                p = fringe.dequeue() # remove from front of the queue
                yield p  # report this position
                for c in self._children(p):
                    fringe.enqueue(c)

    def _return_root(self, tree):
        if not tree.is_empty():
            return self._make_position(tree.root)


    def _find_kmp_more_index(self, T, P):
        """Return the lowest index of T at which substring P begins (or else -1)."""
        index = []
        n, m = len(T), len(P)  # introduce convenient notations
        if m == 0: return 0  # trivial search for empty string
        fail = self._compute_kmp_fail(P)  # rely on utility to precompute
        j = 0  # index into text
        k = 0  # index into pattern
        while j < n:
            if T[j] == P[k]:  # P[0:1+k] matched thus far
                if k == m - 1:  # match is complete
                    index.append(((j - m + 1), (j + 1)))
                    k = fail[k - 1]
                j += 1  # try to extend match
                k += 1
            elif k > 0:
                k = fail[k - 1]  # reuse suffix of P[0:k]
            else:
                j += 1
        if not index:
            return None
        return index


    def _compute_kmp_fail(self, P):
        """Utility that computes and returns KMP 'fail' list."""
        m = len(P)
        fail = [0] * m  # by default, presume overlap of 0 everywhere
        j = 1
        k = 0
        while j < m:  # compute f(j) during this pass, if nonzero
            if P[j] == P[k]:  # k + 1 characters match thus far
                fail[j] = k + 1
                j += 1
                k += 1
            elif k > 0:  # k follows a matching prefix
                k = fail[k - 1]
            else:  # no match found starting at j
                j += 1
        return fail

    def _is_substring(self, start_s1, len_s1, start_s2, len_s2):
        if start_s1 not in range(start_s2, start_s2+len_s2):
            return False
        else:
            if len_s1 > len_s2 - (start_s1 - start_s2):
                return False
            else:
                return True

    def select_all_maximal(self, c):
        count = 0
        n_element = 0
        all_element = {}

        for i in range(len(c)):  # O(len c)
            # prendo la radice
            actual_node = self.suffixTree._childwithoutexception(self.suffixTree._root(), c[i:i + 1])
            if actual_node is None:
                continue
            actual_position = self.suffixTree._make_position(actual_node)
            label = self.suffixTree.getNodeLabel(actual_position)
            len_label = len(label)

            j = 0
            while j != -1:  # O(len c)
                while j < len_label and j != -1:
                    # print("count: " + str(count) + " len_label: " + str(len_label) + " j: " + str(j))
                    if label[j] == c[i:i + 1]:
                        i = i + 1
                        j = j + 1
                        count = count + 1
                        if count >= self.threshold:
                            stop = actual_node._stopIndex - (len_label - j)
                            start = stop - (actual_node._depth - (len_label - j))
                            if start not in all_element:
                                all_element[start] = set()
                            all_element[start].add(stop)
                            n_element = n_element + 1
                    else:
                        count = 0
                        j = -1
                if j == -1:
                    break
                # print("count: " + str(count) + " len_label: " + str(len_label) + " j: " + str(j))
                actual_node2 = self.suffixTree._childwithoutexception(actual_position, c[i:i + 1])
                if actual_node2 is None:
                    if count >= self.threshold:
                        stop = actual_node._stopIndex
                        start = stop - actual_node._depth
                        if start not in all_element:
                            all_element[start] = set()
                        all_element[start].add(stop)
                        n_element = n_element + 1
                    count = 0
                    break
                else:
                    actual_node = actual_node2
                actual_position = self.suffixTree._make_position(actual_node)
                label = self.suffixTree.getNodeLabel(actual_position)
                len_label = len(label)
                j = 0
        return all_element



######## PRIVATE BEHAVIOR #################


######## PUBLIC BEHAVIOR #############

    def __init__(self, s, I):
        self.Contaminants = heap_priority_queue.HeapPriorityQueue()
        self.dna = s
        self.threshold = I
        self.sign = -1
        self.suffixTree = SuffixTree((self.dna,))  #O(len(s)^2)


    def getContaminants(self,k):
        """it returns the k contaminants with larger degree of contamination among the added contaminants.
        La complessità computazionale della proposta è O(k+log(m))"""
        Contaminant_set = []
        Contaminant_reinsert = []
        for i in range(k):
            min_contaminant = self.Contaminants.remove_min()
            Contaminant_reinsert.append(min_contaminant)
            Contaminant_set.append(min_contaminant[1])
        for i in range(k):
            self.Contaminants.add(Contaminant_reinsert[i][0],Contaminant_reinsert[i][1])
        return Contaminant_set

    def addContaminants(self,c):
        """
        Ho una fase di preprocessing nell'init per questo non ricreo l'albero
        """

        #seleziono tutti i massimali -> O(len(C)^2)
        all_maximal = self.select_all_maximal(c)


        #print("Tutti gli elementi massimali: \n" + str(all_maximal))

        processed_string = []

        string_KMP_T = c            #KMP Text
        string_KMP_P = self.dna     #KMP Pattern

        for k,v in all_maximal.items():     #questi due for hanno come somma
            for val in v:                   #O(n_maximal)
                _found = self._find_kmp_more_index(string_KMP_T, string_KMP_P[k:val])  #O[len(s) + len(c)]
                #print("ritorno da KMP: " + str(_found))
                if _found is None:
                    continue
                for str_to_check in _found:                                         #O[n_occurrency]
                    start_index = str_to_check[0]
                    len_string = str_to_check[1] - start_index
                    #print("\nstringa attuale: (" + str(start_index) + ", " + str(len_string) + ")")
                    if not processed_string:
                        #print("Lista vuota: Inserisco: (" + str(start_index) + ", " + str(len_string) + ")")
                        processed_string.append(((start_index, len_string)))
                    else:
                        #print("Lista non vuota: " + str(processed_string) )
                        can_add_new = False
                        can_remove_old = False
                        isFoundAlmostOne = False
                        to_remove = []
                        for e_proc_string in processed_string:                      #O[n_maximal_in_text]
                            start_in_list = e_proc_string[0]
                            len_in_list = e_proc_string[1]
                            #print("Sto confrontando: (" + str(start_in_list) + ", " + str(len_in_list) + ")")

                            #caso 1: l ho "ciao" e voglio inserire "ciao"
                            if (self._is_substring(start_index, len_string, start_in_list, len_in_list)
                                and
                                self._is_substring(start_in_list, len_in_list, start_index, len_string)):

                                can_add_new = False
                                isFoundAlmostOne = True
                                continue

                            # caso 2: l ho "ciao" e voglio inserire "ci"
                            if (self._is_substring(start_index, len_string, start_in_list, len_in_list)
                                and
                                not self._is_substring(start_in_list, len_in_list, start_index, len_string)):

                                can_add_new = False
                                isFoundAlmostOne = True
                                continue

                            # caso 3: l ho "ci" e voglio inserire "ciao"
                            if (not self._is_substring(start_index, len_string, start_in_list, len_in_list)
                                and
                                self._is_substring(start_in_list, len_in_list, start_index, len_string)):
                                isFoundAlmostOne = True
                                can_add_new = False
                                to_remove.append((start_in_list, len_in_list))
                                can_remove_old = True
                                if (start_index, len_string) not in processed_string:
                                    can_add_new = True
                                continue

                            # caso 4: l ho "ciao" e voglio inserire "prova"
                            if (not self._is_substring(start_index, len_string, start_in_list, len_in_list)
                                and
                                not self._is_substring(start_in_list, len_in_list, start_index, len_string)):

                                #Se il massimale non è presente e non è stata trovata nemmeno un'occorrenza allora
                                #lo aggiungo in coda
                                if not isFoundAlmostOne:
                                    if (start_index, len_string) not in processed_string:
                                        can_add_new = True
                                continue

                        if can_add_new:
                            processed_string.append((start_index, len_string))
                        if can_remove_old:
                            for x in to_remove:
                                processed_string.remove(x)

        #print("\nproc string:")
        #print(processed_string)
        #print("len: " + str(len(processed_string)) + ", occurrence: " + str(processed_string) + "\n")

        if len(processed_string) > 0:
            self.Contaminants.add(self.sign * len(processed_string), c)
        return



#DNA = DNAContamination('acgtatcgatg',3)
#DNA.addContaminants('cgtgatga')

#DNA = DNAContamination('cgatgc',3)
#DNA.addContaminants('gatg')

#DNA = DNAContamination('ciaogeciao',2)
#DNA.addContaminants('ciaoociaogiao')

#DNA = DNAContamination('TGGTGTATGAGCTACCAGCCGTGCGAAACTCATACTATTATCTAATCAGGGACAATACCTCAGGCAGGACTGTGCTGTGTAGATAGCTGGAGAGTATTTCTGATTGTCTCCGAGGGGTGTAAAGGTACTTGCAAGGCCACTCAACTCATGCAGCGTTTCCATTTGAGTTGGCCTTAGTAAACGTCAACGCAGCTGGGAGTAGTACCTCTTGGAGGTTGTGACCGCCGCTGCCCGCATGGACAGACGCACGGAAATGTATTAACACTAACTATACT',7)

#1764
#DNA.addContaminants('TGTGTGTGTAGTGTGTGGTGTGTAGTGTGTAGTGTGGTATGTGTGTAGTGCGTGGTGTGTAGTATGTGTGGTGTGTAGTGTGTAGTGTGGTGTGTGTGTAGTGTGTGGTGGGTAGTGTGTAGTGTGGTGTGTAGTGTGTACTGTGTGGTGTGTAGTGTGTGTGGTGTGTACTGTGTAGTGTGGTATGTGTGTAGTGTATGGTGTGTAGTGTGGTGTGTGTGTGGTGTGTAGTGTGTAGTGTGTGTATGCAGTGT')

#2266
#DNA.addContaminants('GCAGAGCAAAAAGTCTGTCTCAAAAAAAAAAAAAAAAGATGAATGAATTGATATGATAGATAGATGGATAGATAGATAGATAGATAGATAGATAGATAGATAGATAGATGGATGATAGATAGATAGTGGGTGGGAGGTAGATAGAAAGATAAGTGGATGGATGAATGGTTGGTAGGTGGGTGTGTGTATGGATGGATGGAAAGATGGATGGATGGATGGATAGCTAGACAATAGATAGATACATGTGGATGGATAGATGGATACATGGAT')

#5141
#DNA.addContaminants('TACCGTGTGTGGTGTGTAGTGTGTAGTGTGTGGTGTGTGTAGTGTGTGGTGTGTACCGTGTGTGGTGTGTAGTGTGTGTGGTGTGTGTGTAGTGTGGTATGTGTGTAGTGTGTGTGGTGTGTAGTGTGTAGTGTGGTGTGTGTGTAGTGTGTGGTGTGTACTGTGTAGTGTGGTGTGTGTGTAGTGTGTGGTGTGTAGTGTGTAGTGTCGTATGTGTTTAGTGTGTGGTGTGTAGTATGTGTGGTGTGTAGTGTGTAGTGTGGTGTGTGTG')

#5141
#DNA.addContaminants('TACCGTGTGTGGTGTGTAGTGTGTAGTGTGTGGTGTGTGTAGTGTGTGGTGTGTACCGTGTGTGGTGTGTAGTGTGTGTGGTGTGTGTGTAGTGTGGTATGTGTGTAGTGTGTGTGGTGTGTAGTGTGTAGTGTGGTGTGTGTGTAGTGTGTGGTGTGTACTGTGTAGTGTGGTGTGTGTGTAGTGTGTGGTGTGTAGTGTGTAGTGTCGTATGTGTTTAGTGTGTGGTGTGTAGTATGTGTGGTGTGTAGTGTGTAGTGTGGTGTGTGTG')






















