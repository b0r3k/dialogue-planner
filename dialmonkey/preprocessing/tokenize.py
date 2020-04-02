#!/usr/bin/env python3


import regex
import unidecode
from ..component import Component


class Tokenizer(Component):

    def __init__(self, config=None):
        super(Tokenizer, self).__init__(config)

        self.lowercase = self.config.get('lowercase', True)
        self.language = self.config.get('language')

        self.normalize = None
        if self.language == 'en':
            self.normalize = self.normalize_en
        elif self.language == 'cs':
            self.normalize = self.normalize_cs
            self.strip_diacritics = self.config.get('strip_diacritics', True)

    def normalize_en(self, toks):
        """Normalization functions for English."""
        # XXX change don't -> do not, I'm -> I am etc.?

        # keep apostrophes together with words in most common contractions
        toks = regex.sub(r'([\'’´]) (s|m|d|ll|re|ve)\s', r' \1\2 ', toks)  # I 'm, I 've etc.
        toks = regex.sub(r'(n [\'’´]) (t\s)', r' \1\2 ', toks)  # do n't

        # other contractions, as implemented in Treex
        toks = regex.sub(r' ([Cc])annot\s', r' \1an not ', toks)
        toks = regex.sub(r' ([Dd]) \' ye\s', r' \1\' ye ', toks)
        toks = regex.sub(r' ([Gg])imme\s', r' \1im me ', toks)
        toks = regex.sub(r' ([Gg])onna\s', r' \1on na ', toks)
        toks = regex.sub(r' ([Gg])otta\s', r' \1ot ta ', toks)
        toks = regex.sub(r' ([Ll])emme\s', r' \1em me ', toks)
        toks = regex.sub(r' ([Mm])ore\'n\s', r' \1ore \'n ', toks)
        toks = regex.sub(r' \' ([Tt])is\s', r' \'\1 is ', toks)
        toks = regex.sub(r' \' ([Tt])was\s', r' \'\1 was ', toks)
        toks = regex.sub(r' ([Ww])anna\s', r' \1an na ', toks)

        return toks

    def normalize_cs(self, toks):
        """Normalization functions for Czech."""
        if self.strip_diacritics:
            toks = unidecode.unidecode(toks)  # this removes all accents
        return toks

    def tokenize(self, text):
        """Tokenize the given text (i.e., insert spaces around all tokens)"""

        if self.lowercase:
            text = text.lower()

        toks = ' ' + text + ' '  # for easier regexes

        # enforce space around all punct
        toks = regex.sub(r'(([^\p{IsAlnum}\s\.\,−\-])\2*)', r' \1 ', toks)  # all punct (except ,-.)
        toks = regex.sub(r'([^\p{N}])([,.])([^\p{N}])', r'\1 \2 \3', toks)  # ,. & no numbers
        toks = regex.sub(r'([^\p{N}])([,.])([\p{N}])', r'\1 \2 \3', toks)  # ,. preceding numbers
        toks = regex.sub(r'([\p{N}])([,.])([^\p{N}])', r'\1 \2 \3', toks)  # ,. following numbers
        toks = regex.sub(r'(–-)([^\p{N}])', r'\1 \2', toks)  # -/– & no number following
        toks = regex.sub(r'(\p{N} *|[^ ])(-)', r'\1\2 ', toks)  # -/– & preceding number/no-space
        toks = regex.sub(r'([-−])', r' \1', toks)  # -/– : always space before

        # language-specific normalization
        if self.normalize:
            toks = self.normalize(toks)

        # clean extra space
        toks = regex.sub(r'\s+', ' ', toks)
        toks = toks.strip()
        return toks

    def __call__(self, dial, logger):
        dial.raw_input = dial.user
        dial.user = self.tokenize(dial.user)
        return dial
