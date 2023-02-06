from sys import argv
from math import log


# Implement your code here #


class Rule:
    def __init__(self, index, source: '', target: [], prob: float):
        self.index = index
        self.source = source
        self.target = target
        self.probability = prob


class Chart:
    def __init__(self, prob: float = 0, rule: Rule = None, left=None, right=None):
        self.probability = prob
        self.rule = rule
        self.left = left
        self.right = right
        self.is_terminal = False
        self.text = None


def split_line(line: ""):
    return line.strip().split()


class Grammars:
    def __init__(self):
        self.rules = []
        self.reversed = {}

    def add_rules(self, grammars_file: ""):
        with open(grammars_file) as rules_file:
            for i, line in enumerate(rules_file):
                words = split_line(line)
                prob = float(words[0])
                source = words[1]
                target = words[3:]
                reversed_key = tuple(target)
                rule = Rule(i, source, reversed_key, prob)
                self.rules.append(rule)
                if self.reversed.get(reversed_key) is None:
                    self.reversed[reversed_key] = []
                self.reversed[reversed_key].append(rule)

    def possible_rules(self, targets: ()):
        return self.reversed.get(targets, [])


space = "    "


class Tree:
    def __init__(self):
        self.tree = ""

    def parsing_tree(self, chart: Chart, ind=0):
        if chart.is_terminal:
            self.tree += f'\n{ind * space}{chart.rule.source} > {chart.text}'
            return
        self.tree += f'\n{ind * space}{chart.rule.source}'
        self.parsing_tree(chart.left, ind + 1)
        self.parsing_tree(chart.right, ind + 1)


# CKY as we learned in lecture getting sentence and grammar rules
def cky(sent: "", grammar_rule: Grammars):
    # Split to words
    words = split_line(sent)
    n = len(words)
    chart = [[[Chart() for _ in range(len(grammar_rule.rules))] for _ in range(n + 1)] for _ in range(n)]

    for col in range(1, n + 1):
        word = words[col - 1]
        for rule in grammar_rule.possible_rules((word,)):
            chart[col - 1][col][rule.index].rule = rule
            chart[col - 1][col][rule.index].probability = rule.probability
            chart[col - 1][col][rule.index].text = word
            chart[col - 1][col][rule.index].is_terminal = True

        for row in range(col - 2, -1, -1):
            for k in range(row + 1, col):
                for i in [rule for rule in grammar_rule.rules if chart[row][k][rule.index].probability > 0]:
                    for j in [rule for rule in grammar_rule.rules if chart[k][col][rule.index].probability > 0]:
                        for rule in grammar_rule.possible_rules((i.source, j.source)):
                            p = rule.probability * chart[row][k][i.index].probability * chart[k][col][
                                j.index].probability
                            if p > chart[row][col][rule.index].probability:
                                chart[row][col][rule.index].probability = p
                                chart[row][col][rule.index].rule = rule
                                chart[row][col][rule.index].left = chart[row][k][i.index]
                                chart[row][col][rule.index].right = chart[k][col][j.index]
    cell = chart[0][n][0]
    parse_tree = Tree()
    if cell.probability > 0:
        parse_tree.parsing_tree(cell)
        return parse_tree.tree, log(cell.probability)
    return None, None


if __name__ == '__main__':

    input_grammar = argv[1]  # The name of the file that contains the probabilistic grammar
    input_sentences = argv[2]  # The name of the file that contains the input sentences (tests)
    output_trees = argv[3]  # The name of the output file

    # Implement your code here #

    grammar = Grammars()
    grammar.add_rules(input_grammar)
    output = []
    with open(input_sentences) as file:
        for sentence in file:
            output.append(f'Sentence: {sentence}')
            tree, probability = cky(sentence, grammar)
            if probability is None:
                output.append("***This sentence is not a member of the language generated by the grammar ***\n\n")
            else:
                output.append(f'Parsing:{tree}\n')
                output.append(f"Log Probability: {probability}\n\n")
    result_str = ''.join(output)
    with open(output_trees, 'w', encoding='utf8') as output_file:
        output_file.write(result_str)