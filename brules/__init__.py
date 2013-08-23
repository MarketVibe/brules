import re


class UnmatchedRuleError(Exception):
    pass


class RuleSet(object):
    def __init__(self):
        self._rules = []
        self._multiline_rules = []

    def add_rule(self, pattern, func):
        self._rules.append((re.compile(pattern), func))

    def add_multiline_rule(self, pattern, func):
        self._multiline_rules.append((re.compile(pattern), func))

    def parse(self, toparse):
        matches = []
        i = 0
        end = len(toparse)
        while i < end:
            try:
                match, i = self._match_multiline(toparse, i)
            except UnmatchedRuleError:
                line_end = toparse.find('\n', i)
                if line_end == -1:
                    line_end = end
                match = self._match_line(toparse[i:line_end])
                i = line_end + 1
            matches.append(match)
        return matches

    def _match_multiline(self, tomatch, start):
        for pattern, func in self._multiline_rules:
            match = pattern.match(tomatch, start)
            if match:
                match_dict = self._combined_match_dict(match)
                end = match.end()
                return (match_dict, func), end

        raise UnmatchedRuleError(
            'No matching rules at "{}"'.format(tomatch.split(None, 1)[0]))

    def _match_line(self, line):
        for pattern, func in self._rules:
            match = pattern.search(line)
            if match:
                match_dict = self._combined_match_dict(match)

                start = match.start()
                end = match.end()

                if start:
                    match_dict['prefix_content'] = line[:start]
                if end < len(line):
                    match_dict['suffix_content'] = line[end:]

                return (match_dict, func)

        raise UnmatchedRuleError('No matching rules for "{}"'.format(line))

    def _combined_match_dict(self, match):
        match_dict = match.groupdict()
        match_dict.update(enumerate(match.groups(), start=1))
        return match_dict
