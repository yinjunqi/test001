#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: lexparser.py
"""
import copy
import json
import pdb
import re
import logging
import sys

try:
    from slot_tree import SlotTree
    from pattern_tree import PatternTree
except:
    from .slot_tree import SlotTree
    from .pattern_tree import PatternTree


class LexparserNode(object):
    """ LexparserNode class """

    def __init__(self):
        """

        the codec of all value is unicode
        For example:
            curr_word: today      //the text that is recognized
            next_text: is Monday  //the following text that need to be parse
            slot: [D:date]        //the recognized slot of 'today', may be empty
            pattern_tree: PatternTree object  //current patern_tree
            pre_node: LexparserNode object          //previous Node
            intent_name: ''                   //the intent that pattern matchs, may be empty
        """
        self.curr_word = ''
        self.next_text = ''
        self.slot = ''
        self.pattern_tree = None
        self.pre_node = None
        self.intent_name = ''


class LexParser(object):
    """ lexparser class """

    def __init__(self):
        """ init function """
        pass

    def load(self, patterns_file, slots_file):
        """ load pattern and slot file """
        self.pattern_tree = PatternTree()
        self.slot_tree = SlotTree()
        patterns = open(patterns_file,encoding='utf-8')
        intent_name = ''
        for line in patterns:
            line = line.strip()
            iname = re.match(r'\[@(\w+)\]', line)
            if iname:
                intent_name = line.strip('[]@')
            else:
                normal_texts = self.pattern_tree.add_tree(line, intent_name)
                for i, val in enumerate(normal_texts):
                    self.slot_tree.add_tree(val, 'NormalText', is_unicode=True)
        patterns.close()
        slots = open(slots_file,encoding='utf-8')
        slot_name = ''
        for line in slots:
            line = line.strip()
            slot, _ = self.pattern_tree.get_slot(line)
            if slot:
                slot_name = slot
            else:
                self.slot_tree.add_tree(line, slot_name)
        slots.close()
        logging.debug(json.dumps(self.pattern_tree.tree, ensure_ascii=False).encode('utf8'))
        logging.debug(json.dumps(self.slot_tree.tree, ensure_ascii=False, default=self.set_default).encode('utf8'))

    def set_default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError

    def match_pattern(self, obj):
        """ return pattern of obj """
        ptree = obj.pattern_tree
        text = obj.next_text
        if text:
            return ''
        if 'intent' not in ptree.tree:
            return ''
        return ptree.tree['intent']

    def parse(self, text):
        """
        return: {
                'intent': <intent>
                'slots': [{
                    'type': <slot_type>,
                    'original_word': <word>
                    }]
        """
        # the codec of text is utf8
        # text = text.decode('utf8')
        root = LexparserNode()
        root.next_text = text
        root.pattern_tree = self.pattern_tree

        candidates = [root]
        results = []
        while len(candidates) > 0:
            # pdb.set_trace()
            ### Do slot tree search ###
            cand = candidates[0]
            text = cand.next_text
            tlen = len(text)
            ptree = cand.pattern_tree
            ### process WildCards ###
            if 'WILDTREE' in ptree.tree:
                ## has WildCards ##
                wildtree = ptree.tree['WILDTREE']
                for wcard in wildtree:
                    # pdb.set_trace()
                    wtree = wildtree[wcard]
                    logging.debug("************")
                    logging.debug(wcard)
                    logging.debug(json.dumps(wtree, ensure_ascii=False).encode('utf8'))
                    lower = wtree['lower']
                    upper = wtree['upper']
                    while lower <= upper and lower <= tlen:
                        obj = LexparserNode()
                        obj.curr_word = text[:lower]
                        # logging.debug("curr_word:" + obj.curr_word.encode('utf8'))
                        logging.debug("curr_word:" + obj.curr_word)
                        obj.slot = "WILD_WORD"
                        obj.next_text = text[lower:]
                        # logging.debug("next:" + obj.next_text.encode('utf8'))
                        logging.debug("next:" + obj.next_text)
                        obj.pre_node = candidates[0]
                        obj.pattern_tree = PatternTree(wtree)
                        if len(obj.next_text) > 0 or "intent" not in wtree:
                            candidates.append(obj)
                        else:
                            results.append(obj)
                        lower = lower + 1
            ## no WildCards
            logging.debug("len of candidates is:%d" % len(candidates))
            self._do_one_step_search(text, ptree, candidates, results)
            candidates.pop(0)
        ###output results
        res_candidates = []
        for i, res in enumerate(results):
            # m = 0
            res_obj = {'intent': '', 'slots': []}
            res_obj['intent'] = res.pattern_tree.tree['intent']
            while res.pre_node:
                if res.slot:
                    obj = {
                        'type': res.slot,
                        'original_word': res.curr_word
                    }
                    res_obj['slots'].insert(0, obj)
                res = res.pre_node
            res_candidates.append(res_obj)
        return res_candidates

    def _do_one_step_search(self, text, ptree, candidates, results):
        """ do Slot tree search """
        logging.debug(" _do_one_step_search text is:%s" % text)
        slot_results = self.slot_tree.prefix_search(text)
        logging.debug(slot_results)
        for j, slot_res in enumerate(slot_results):
            curr_word, slots, next_text = slot_res
            logging.debug("curr_word:%s, slots:%s,next_text:%s" % (curr_word, slots, next_text))
            ### Do pattern tree search ###
            for slot in slots:
                obj = LexparserNode()
                obj.pattern_tree = ptree
                obj.pre_node = candidates[0]
                obj.slot = slot
                obj.curr_word = curr_word
                obj.next_text = next_text
                next_pt = None
                if obj.slot == 'NormalText':
                    next_pt = ptree.search_one_slot(obj.curr_word)
                elif obj.slot:
                    next_pt = ptree.search_one_slot(obj.slot)
                if next_pt:
                    obj.pattern_tree = next_pt
                    ### If it is the matched result: ###
                    if self.match_pattern(obj):
                        ## then output the result
                        results.append(obj)
                    else:
                        ## add new candidates to do slot tree search
                        candidates.append(obj)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s [line:%(lineno)d] '
                               '[%(levelname)s] %(message)s',
                        datefmt='%H:%M:%S',
                        stream=sys.stdout,
                        filemode='w')
    lp = LexParser()
    lp.load('./data/pattern', './data/slots')

    query = '我朋友知道懂法守法买保险'
    print(query)
    print(json.dumps(lp.parse(query), ensure_ascii=False))
    # print(json.dumps(lp.parse(query), ensure_ascii=False).encode('utf8'))

    query = '怎么买保险'
    print(query)
    print(json.dumps(lp.parse(query), ensure_ascii=False))
    # print(json.dumps(lp.parse(query), ensure_ascii=False).encode('utf8'))

    query = '介绍一下平安福'
    print(query)
    print(json.dumps(lp.parse(query), ensure_ascii=False))
    # print(json.dumps(lp.parse(query), ensure_ascii=False).encode('utf8'))

    query = '不要给我推荐保险'
    print(query)
    print(json.dumps(lp.parse(query), ensure_ascii=False))
    # print(json.dumps(lp.parse(query), ensure_ascii=False).encode('utf8'))
    print("END")
