#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""
import pdb


class SlotTree(object):
    """ SlotTree class """

    def __init__(self, tree=None):
        """ init function """
        if tree and isinstance(tree, dict):
            self.tree = tree
        else:
            self.tree = {}

    def add_tree(self, word, value='default', is_unicode=False):
        """ add element to tree """
        # tree = {}
        tree = self.tree
        # if not is_unicode:
        #     word = word.decode('utf8')
        for char in word:
            if char in tree:
                tree = tree[char]
            else:
                tree[char] = {}
                tree = tree[char]
        if 'exist' not in tree:
            tree['exist'] = {value}
        else:
            tree['exist'].add(value)

    def get_tree(self):
        """ return tree """
        return self.tree

    def prefix_search(self, word, is_unicode=True):
        """
        return: a list of all results
            [(prefix,value,next),()]
        """
        # if not is_unicode:
        #     word = word.decode('utf8')
        tree = self.tree
        results = []
        for i in range(len(word)):
            char = word[i]
            if char in tree:
                tree = tree[char]
                if 'exist' in tree:
                    if i == len(word) - 1:
                        pre = word
                        next = ''
                    else:
                        pre = word[0: i + 1]
                        next = word[i + 1:]
                    results.append((pre, tree['exist'], next))
            else:
                # ill char
                return results
        return results


if __name__ == '__main__':
    tree = SlotTree()
    test_str = '今天天气不错'
    tree.add_tree(test_str, '[D:query]')
    test_str = '今天天气不错2'
    tree.add_tree(test_str, '[D:query]')
    tree.add_tree('abc')
    tree.add_tree('ab')
    print(tree.tree)
    # Print {'a': {'b': {'c': {'exist': True}}}, 'b': {'c': {'d': {'exist': True}}}}
    print(tree.prefix_search("ab"))
    # Print False
    print(tree.prefix_search('abc'))
    # Print Tree
    t = (tree.prefix_search('今天天气不错2', False))
    print(t)
    # Print True
