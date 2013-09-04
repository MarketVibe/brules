from .common import UnmatchedStepError, combined_match_dict
import re


class Step(object):
    def parse(self, toparse, start_index):
        raise NotImplementedError('Step subclasses must implement parse')

    def __call__(self, context, args):
        raise NotImplementedError('Step subclasses must implement __call__')


class RegexStep(Step):
    def __init__(self, regex, multiline=False):
        self.multiline = multiline
        self.regex = re.compile(regex)

    def parse(self, toparse, start_index):
        if self.multiline:
            return self.parse_multiline(toparse, start_index)
        else:
            return self.parse_line(toparse, start_index)

    def parse_multiline(self, toparse, start_index):
        match = self.regex.match(toparse, start_index)
        if match:
            match_dict = combined_match_dict(match)
            end = match.end()
            return (match_dict, self), end
        line = toparse[start_index:].split('\n', 1)[0]
        raise UnmatchedStepError('Step does not match at "{}"'.format(line))

    def parse_line(self, toparse, start_index):
        end = len(toparse)
        line_end = toparse.find('\n', start_index)
        if line_end == -1:
            line_end = end
        line = toparse[start_index:line_end]
        match = self.regex.search(line)
        if match:
            match_dict = combined_match_dict(match)

            start = match.start()
            end = match.end()

            if start > 0:
                match_dict['prefix_content'] = line[:start]
            if end < len(line):
                match_dict['suffix_content'] = line[end:]

            return (match_dict, self), line_end + 1
        raise UnmatchedStepError('Step does not match at "{}"'.format(line))


class RegexFuncStep(RegexStep):
    def __init__(self, regex, func, multiline=False):
        super(RegexFuncStep, self).__init__(regex, multiline)
        self.func = func

    def __call__(self, context, args):
        return self.func(context, args)

    @classmethod
    def make(cls, regex, multiline=False):
        """Decorator which wraps the specified regex and func in a
        RegexFuncStep instance
        """
        def make_inst(func):
            return cls(regex, func, multiline)

        return make_inst
