#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: TrieTree.py
"""
import pdb
import json
import re


class PatternTree(object):
    """ PatternTree class """

    def __init__(self, tree=None):
        """ init function """
        if tree:
            self.tree = tree
        else:
            self.tree = {}

    def add_tree(self, text, value='default'):
        """ add element to tree """
        # text = text.decode('utf8')
        tree = self.tree
        normal_texts = []
        while text != '':
            key = ''
            lower, upper, new_text = self.get_wildcard(text)
            # print("lower %d,upper%d,new_text%s" % (lower,upper,new_text))
            if lower != -1 and upper != -1:
                key = "[W:%d-%d]" % (lower, upper)
                if 'WILDTREE' not in tree:
                    tree['WILDTREE'] = {}
                wild_tree = tree['WILDTREE']
                if key in wild_tree:
                    tree = wild_tree[key]
                else:
                    wild_tree[key] = {}
                    tree = wild_tree[key]
                    tree['upper'] = upper
                    tree['lower'] = lower
                text = new_text
            else:
                slot, new_text = self.get_slot(text)
                # print "slot%s, new_text%s" % (slot,new_text)
                if slot:
                    key = slot
                    text = new_text
                    # tree['has_slot'] = True
                else:
                    normal_text, new_text = self.get_normal_text(text)
                    # print "normal_text%s, new_text%s" % (normal_text,new_text)
                    if not normal_text:
                        return None
                    normal_texts.append(normal_text)
                    key = normal_text
                    text = new_text
                    tree['has_text'] = True
                if key in tree:
                    tree = tree[key]
                else:
                    tree[key] = {}
                    tree = tree[key]
        tree['intent'] = value
        return normal_texts

    def get_slot(self, text):
        """ get slot for text """
        if text[0] == '[' and text[1] == 'D' and text[2] == ':':
            p = text[3:]
            slot = '[D:'
            flag = False
            for i in range(len(p)):
                char = p[i]
                slot = slot + char
                if char == ']':
                    text = text[i + 4:]
                    flag = True
                    break
            if not flag:
                return None, text
            # else:
            # cannot find ']'
            #    return None, text
            return slot, text
        return None, text

    def get_wildcard(self, text):
        """ parse text with wildcard 
        """
        pattern = re.compile('^\[W:(\d+)-(\d+)\](.*)', re.U)
        ret = pattern.search(text)
        if not ret:
            return -1, -1, text
        lower, upper, next_text = ret.groups()
        l = int(lower)
        u = int(upper)
        if l > u:
            return -1, -1, text
        return l, u, next_text

    def get_normal_text(self, text):
        """ get normal text """
        text_len = len(text)
        for i in range(text_len):
            char = text[i]
            if char == '[':
                return text[0:i], text[i:]
            elif i == text_len - 1:
                return text, ''

    def get_tree(self):
        """ get tree """
        return self.tree

    def print_tree(self):
        """ print tree of json format """
        print(json.dumps(self.tree, ensure_ascii=False).encode('utf8'))

    def print_child_tree(self, tree):
        """ print tree of json format """
        print(json.dumps(tree, ensure_ascii=False).encode('utf8'))

    def search_one_slot(self, slot):
        """ search slot from tree """
        tree = self.tree
        if slot in tree:
            tree = tree[slot]
        else:
            return None
        return PatternTree(tree)

    #    def search_by_chars(self, text):
    #        """
    #        return: list of all possible results
    #            [(PatternTree, next_text)]
    #        """
    #        tree = self.tree
    #        results = []
    #        text_len = len(text)
    #        for i in xrange(text_len):
    #            char = text[i]
    #            pre_text  = text[0:i+1]
    #            next_text = None
    #            if i + 1 < text_len:
    #                next_text = text[i+1:]
    #            if char in tree:
    #                tree = tree[char]
    #                if 'has_slot' in tree:
    #                    results.append((PatternTree(tree), pre_text, next_text))
    #                elif not next_text and ('intent' in tree):
    #                    results.append((PatternTree(tree), pre_text, None))
    #            else:
    #                break
    #        return results
    def search(self, text, is_unicode=True):
        """ search text """
        if not is_unicode:
            text = text.decode('utf8')
        tree = self.tree
        while text != '':
            char = ''
            slot, new_text = self.get_slot(text)
            if slot:
                char = slot
                text = new_text
            else:
                char = text[0]
            print("inside_char:[%s], text:[%s]" % (char, text))
            if char in tree:
                tree = tree[char]
                text = text[1:]
            else:
                ## meet illegal char
                return PatternTree(tree), text
        ## search end
        if 'intent' in tree and tree['intent'] == True:
            return PatternTree(tree), None
        else:
            return PatternTree(tree), None


if __name__ == '__main__':
    raw_tree = PatternTree()
    tree = raw_tree
    p = '[D:asdfasdlfkjalsdkjf][W:0-20][D:city][W:0-20]'
    pp = tree.add_tree(p,'asv')
    print("pp:",pp)
    print('1')
    tree.print_tree()
    # {"[D:asdfasdlfkjalsdkjf]": {"WILDTREE": {"[W:0-20]": {"upper": 20, "lower": 0, "[D:city]": {"intent": "default"}}}}}
    _tree, not_cover_text = tree.search('[D:asdfasdlfkjalsdkjf]nisha')
    print('2')
    tree.print_child_tree(_tree.get_tree())
    print("not_cover_text:%s" % (not_cover_text))
    _tree, not_cover_text = tree.search('[D:city1]')
    print('3')
    tree.print_child_tree(_tree.get_tree())
    print("not_cover_text:%s" % (not_cover_text))

    _tree, not_cover_text = tree.search('[W:0-20]')
    print('4')
    tree.print_child_tree(_tree.get_tree())
    print("not_cover_text:%s" % (not_cover_text))
    tree.add_tree('123')
    print(tree.get_slot("abc"))
    tree.print_tree()
    raw_tree.print_tree()
