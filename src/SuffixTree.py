"""
1) Consider the ADT SuffixTree with the following interface:
● SuffixTree(S): it creates a Suffix Tree starting from the tuple S of strings; each node
of the tree, except the root, is marked with a reference to those strings in S for which
there is a suffix going through node u; moreover, the substring associated to each
node must not be explicitly represented in the tree (to this aim, S can be assumed to
be an immutable object);
● T.getNodeLabel(P): it returns the substring that labels the node of T to which
position P refers (it throws an exception if P is invalid);
● T.pathString(P): it returns the substring associated to the path in T from the root to
the node to which position P refers (it throws an exception if P is invalid);
● T.getNodeDepth(P): it returns the length of substring associated to the path in T
from the root to the node to which position P refers (it throws an exception if P is
invalid);
● T.getNodeMark(P): it returns the mark of the node u of T to which position P refers
(it throws an exception if P is invalid);
● T.child(P, s): it returns the position of the child u of the node of T to which position P
refers such that
○ either s is a prefix of the substring labeling u,
○ or the substring labeling u is a prefix of s,
if it exists, and it returns None otherwise (it throws an exception if P is invalid or s is
empty).
"""
from TdP_collections.queue.array_queue import ArrayQueue
from TdP_collections.tree import tree


class SuffixTree(tree.Tree):
    ######## PRIVATE #################

    class _Node:
        def __init__(self, substring, parent=None, depth=None, start=None, stop=None, firstmark=None):
            self._substring = substring
            self._parent = parent
            self._children = {}
            self._depth = depth
            self._mark = {}
            self._firstmark = firstmark
            self._startIndex = start
            self._stopIndex = stop

    class _Position(tree.Tree.Position):
        def __init__(self, container, node):
            self._container = container
            self._node = node

        def element(self):
            return str(self._node._firstmark) + "," + str(self._node._startIndex) + ":" + str(
                self._node._stopIndex) + "  all marks: " + str(self._node._mark.keys())

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

    def _suffix(self, s):
        """returns a list containing s'suffixies"""
        suffixies = []
        j = 0
        for i in range(len(s) - 1, -1, -1):
            suffixies.insert(j, s[i:])
            j = j + 1
        return suffixies

    def _addmark(self, node, mark, start=None, stop=None, value=True):
        node._mark[mark] = value
        if node._firstmark is None:
            node._firstmark = mark
        if start is not None:
            node._startIndex = start
        if stop is not None:
            node._stopIndex = stop

    def _copymark(self, node, parent, start=None, stop=None, firstmark=None):
        node._mark = parent._mark.copy()
        if firstmark is not None:
            node._firstmark = firstmark
        else:
            node._firstmark = parent._firstmark
        if start is not None:
            node._startIndex = start
        if stop is not None:
            node._stopIndex = stop

    def _longcommonprefix(self, child, suffix):
        word = self.S[child._firstmark]
        count = 0
        if child._stopIndex - child._startIndex < len(suffix):
            less = child._stopIndex - child._startIndex
        else:
            less = len(suffix)
        for i in range(child._startIndex, child._startIndex + less):
            if word[i] == suffix[i - child._startIndex]:
                count = count + 1
            else:
                return count
        return count

    def _insert(self, ref_node, substring, string_mark, string_lenght):
        # controlla se ho il figlio che ha come primo carattere quello della sottostringa
        if substring[0] not in ref_node._children:  # non è presente nessun figlio
            if ref_node == self.root:  # controlla se sono nella root o in una sotto radice
                # CASO 1 siamo nella root e non ho il figlio che ha come primo carattere quello della sottostringa

                # creo nuovo nodo e associo il padre al figlio e viceversa
                newnode = self._Node(substring=substring, parent=ref_node, depth=len(substring))
                ref_node._children.__setitem__(substring[0], newnode)

                # aggiungo il marcatore al figlio creato (no alla root principale)
                self._addmark(newnode, string_mark, start=string_lenght - len(substring), stop=string_lenght)

                # incremento la dimensione dell'suffix tree
                self.size = self.size + 1
            else:
                # CASO 2 siamo in una sottoradice e non ho il figlio che ha come primo carattere quello della sottostringa

                if '/0' in ref_node._children:
                    # ottengo il nodo terminatore
                    terminator = self._Node(substring='/0', parent=ref_node, depth=ref_node._depth)
                    self._copymark(terminator, ref_node, start=ref_node._stopIndex, stop=ref_node._stopIndex)
                    ref_node._children.__setitem__('/0', terminator)
                    self.size = self.size + 1

                # creo nuovo nodo e associo il padre al figlio e viceversa
                newnode = self._Node(substring=substring, parent=ref_node, depth=len(substring) + ref_node._depth)
                ref_node._children.__setitem__(substring[0], newnode)

                # aggiungo il marcatore al nodo preesistente e al figlio creato
                self._addmark(newnode, string_mark, start=string_lenght - len(substring), stop=string_lenght)
                self._addmark(ref_node, string_mark)

                # incremento la dimensione dell'suffix tree
                self.size = self.size + 1
            return
        else:  # è presente un figlio
            # Prendo il riferimento al nodo figlio
            ref_child = ref_node._children.__getitem__(substring[0])

            # calcolo la lunghezza del più grande prefisso in comune
            LCP = self._longcommonprefix(ref_child, substring)

            # CASO 3 Nel nodo ho "CIAO" e voglio aggiungere "CIAO"
            if LCP == (ref_child._stopIndex - ref_child._startIndex) and LCP == len(substring):
                # aggiungo il marcatore al nodo
                self._addmark(node=ref_child, mark=string_mark)

                # se ci sta un figlio terminatore, aggiungo il mark
                if '/0' in ref_child._children:
                    term_child = ref_child._children.__getitem__('/0')
                    self._addmark(node=term_child, mark=string_mark)

                # se non ci sta un figlio terminatore
                else:
                    # se ci sono già altri figli, allora aggiungo nodo terminatore
                    if len(ref_child._children) > 1:
                        # aggiungo nodo terminatore
                        terminator = self._Node(substring='/0', parent=ref_child, depth=ref_child._depth)
                        ref_child._children.__setitem__('/0', terminator)

                        # aggiungo il marcatore al terminatore
                        self._addmark(node=terminator, mark=string_mark, start=string_lenght, stop=string_lenght)

                        # incremento la dimensione dell'suffix tree
                        self.size = self.size + 1


            # CASO 4 Nel nodo ho "CI" (-> dim 2) e voglio aggiungere "CIAO" (-> dim 4) (LCP = 2)
            elif LCP == (ref_child._stopIndex - ref_child._startIndex) and len(substring) > LCP:
                if len(ref_child._children) == 0:  # se non ci sono figli
                    # aggiungo nodo terminatore
                    terminator = self._Node(substring='/0', parent=ref_child, depth=ref_child._depth)
                    ref_child._children.__setitem__('/0', terminator)

                    # copio i marcatori del padre nel figlio
                    self._copymark(node=terminator, parent=ref_child, start=ref_child._stopIndex,
                                   stop=ref_child._stopIndex)

                    # aggiungo il nuovo nodo
                    new_node = self._Node(substring=substring[LCP:], parent=ref_child,
                                          depth=ref_child._depth + len(substring[LCP:]))
                    ref_child._children.__setitem__(substring[LCP], new_node)

                    # setto i marcatori al padre e al figlio
                    self._addmark(node=ref_child, mark=string_mark)
                    self._addmark(node=new_node, mark=string_mark, start=string_lenght - (len(substring) - LCP),
                                  stop=string_lenght)

                    # incremento la dimensione dell'suffix tree
                    self.size = self.size + 2

                else:
                    # rifaccio al ricorsione sulla sottostringa "AO"
                    self._addmark(node=ref_child, mark=string_mark)
                    self._insert(ref_node=ref_child, substring=substring[LCP:], string_mark=string_mark,
                                 string_lenght=string_lenght)

            # CASO 5 Nel nodo ho "CIAONE" (-> dim 6) e voglio aggiungere "CIAO" (-> dim 4) (LCP = 4)
            elif (ref_child._stopIndex - ref_child._startIndex) > LCP and len(substring) == LCP:
                # aggiungo il nuovo nodo
                new_node = self._Node(
                    substring=self.S[ref_child._firstmark][ref_child._startIndex + LCP: ref_child._stopIndex],
                    parent=ref_child, depth=ref_child._depth)
                ref_child._children.__setitem__(self.S[ref_child._firstmark][ref_child._startIndex + LCP], new_node)

                # copio i marcatori del padre nel figlio
                self._copymark(node=new_node, parent=ref_child, start=ref_child._startIndex + LCP,
                               stop=ref_child._stopIndex)

                # la nuova depth è quella di prima meno la dimensione di "NE"
                ref_child._depth = ref_child._depth - ((ref_child._stopIndex - ref_child._startIndex) - LCP)
                ref_child._stopIndex = ref_child._stopIndex - ((ref_child._stopIndex - ref_child._startIndex) - LCP)

                # aggiungo il mark al nodo "CIAO-NE-"
                self._addmark(node=ref_child, mark=string_mark)

                # aggiungo nodo terminatore
                terminator = self._Node(substring='/0', parent=ref_child, depth=ref_child._depth)
                ref_child._children.__setitem__('/0', terminator)

                # aggiungo il marcatore nel figlio terminatore
                self._addmark(node=terminator, mark=string_mark, start=string_lenght, stop=string_lenght)

                # incremento la dimensione dell'suffix tree
                self.size = self.size + 2

            # CASO 6 Nel nodo ho "CIG" (-> dim 3) e voglio aggiungere "CIAO" (-> dim 4) (LCP = 2)
            elif (ref_child._stopIndex - ref_child._startIndex) > LCP and len(substring) > LCP:
                # creiamo il nodo CI
                new_node_father = self._Node(substring=substring[:LCP], parent=ref_child._parent, depth=ref_child._depth - ((ref_child._stopIndex - ref_child._startIndex) - LCP))

                #associo mark, start e stop index
                self._copymark(node=new_node_father, parent=ref_child, start=ref_child._startIndex, stop=ref_child._stopIndex - ((ref_child._stopIndex - ref_child._startIndex) - LCP))

                # associo il padre al nuovo figlio
                new_node_father._parent._children.__setitem__(self.S[new_node_father._firstmark][new_node_father._startIndex], new_node_father)

                #associo il figlio al nuovo padre
                ref_child._parent = new_node_father

                #cambio lo start, stop e depth del figlio
                #ref_child._depth = ref_child._depth
                ref_child._startIndex = ref_child._startIndex + LCP
                #ref_child._stopIndex = ref_child._stopIndex

                #associo il nuovo padre al nuovo figlio
                new_node_father._children.__setitem__(self.S[ref_child._firstmark][ref_child._startIndex], ref_child)

                #creo il nodo da aggiungere
                node_append = self._Node(substring=substring[LCP], parent=new_node_father, depth=new_node_father._depth + len(substring[LCP:]))

                #lo associo al nuovo padre
                new_node_father._children.__setitem__(substring[LCP], node_append)

                #setto i mark
                self._addmark(node=new_node_father, mark=string_mark)
                self._addmark(node=node_append, mark=string_mark, start=(string_lenght - len(substring)) + LCP, stop=string_lenght)

                self.size = self.size + 2



    def _getNodeLabelFather(self, P):
        node = self._validate(P)
        if node._parent is not None:
            node = node._parent
        else:
            return
        if node._parent is not None:
            if node._startIndex == node._stopIndex:
                return "\\0"
            else:
                return self.S[node._firstmark][node._startIndex:node._stopIndex]
        else:
            return

    def _isPrefixOrSuffix(self, s1, s2):
        less = min(len(s1), len(s2))
        for i in range(0, less):
            if (s1[i] != s2[i]):
                return False
        return True

    def _breadthfirst(self):
        """Generate a breadth-first iteration of the positions of the alberi."""
        if not self.is_empty():
            fringe = ArrayQueue()  # known positions not yet yielded
            fringe.enqueue(self._make_position(self.root))  # starting with the root
            while not fringe.is_empty():
                p = fringe.dequeue()  # remove from front of the queue
                yield p  # report this position
                for c in self._children(p):
                    fringe.enqueue(c)


    ######## PRIVATE BEHAVIOR #################

    ######## private BEHAVIOR FROM TREE #################

    def _root(self):
        """Return Position representing the alberi's root (or None if empty)."""
        return self._make_position(self.root)

    def _parent(self, p):
        """Return Position representing p's parent (or None if p is root)."""
        if self.is_root(p):
            return None
        node = self._validate(p)
        return self._make_position(node._parent)

    def _num_children(self, p):
        """Return the number of children that Position p has."""
        node = self._validate(p)
        return node._children.__len__()

    def _children(self, p):
        """Generate an iteration of Positions representing p's children."""
        node = self._validate(p)
        for child in node._children.values():
            yield self._make_position(child)

    def _childwithoutexception(self, P, s):
        node = self._validate(P)
        if len(s) == 0:
            return None
        if s[0] not in node._children:
            return None
        else:
            child = node._children.__getitem__(s[0])
            if self._isPrefixOrSuffix(self.getNodeLabel(self._make_position(child)), s):
                return child
            else:
                return None

    ######## PUBLIC BEHAVIOR FROM TREE #################

    ######## PUBLIC BEHAVIOR #################
    def __init__(self, S):
        self.root = self._Node(substring="", depth=0)
        self._addmark(self.root, mark=None)
        self.size = 1
        self.S = S
        i = 0
        for word in S:
            suffixies = self._suffix(word)
            for suffix in suffixies:
                self._insert(self.root, suffix, i, len(word))
            i = i + 1

    def __len__(self):
        """Return the total number of elements in the alberi."""
        return self.size


    def getNodeLabel(self, P):
        node = self._validate(P)
        if node._parent is not None:
            if node._startIndex == node._stopIndex:
                return "\\0"
            else:
                return self.S[node._firstmark][node._startIndex:node._stopIndex]
        else:
            return

    def pathString(self, P):
        node = self._validate(P)
        if node._parent is not None:
            return self.pathString(self._make_position(node._parent)) + self.getNodeLabel(P)
        else:
            return ""

    def getNodeDepth(self, P):
        node = self._validate(P)
        return node._depth

    def getNodeMark(self, P):
        node = self._validate(P)
        return node._mark.keys()

    def child(self, P, s):
        node = self._validate(P)
        if len(s) == 0:
            raise ValueError("S is empty")
        if s[0] not in node._children:
            return None
        else:
            child = node._children.__getitem__(s[0])
            if self._isPrefixOrSuffix(self.getNodeLabel(self._make_position(child)), s):
                return child
            else:
                return None

    ######## PUBLIC BEHAVIOR #################


"""
case1 = ('aa', 'ac')
casemidterm = ('acgtatcgatg', 'cgtgatga')
tuple2 = ('alive', 'cali')
tuple3 = ('ciao', 'ciaone')
tuple4 = ('sto', 'stop', 'sto')
# albero = SuffixTree(S)
# albero2 = SuffixTree(('prova','pravo'))

albero = SuffixTree(casemidterm)
print("\n\nInserisco suffix tree: ")
print(casemidterm)
print("")
for i in albero._breadthfirst():
    print("Padre: " + str(albero._getNodeLabelFather(i)) + " Figlio: " + str(albero.getNodeLabel(i)) + " " + i.element())


print("\n\nNode label:")
for i in albero._breadthfirst():
    print(albero.getNodeLabel(i))

print("\n\nDepth + Path string + mark:")
for i in albero._breadthfirst():
    print(str(albero.getNodeDepth(i)) + "\t" + albero.pathString(i) + "\t\t\t\t" + str(albero.getNodeMark(i)))

print("\n\nFigli:")
for i in albero._breadthfirst():
    print(str(albero.getNodeLabel(i)) + "\t\t\t" + str(albero.child(i, "ne")))
"""





















