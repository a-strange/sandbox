import cProfile
from typing import List, Optional

GRID = [
    ['G', 'I', 'Z'],
    ['U', 'E', 'K'],
    ['Q', 'S', 'E']
]

WORD_DICT = {'GEEKS', 'FOR', 'QUIZ', 'GO', 'SEEK'}


class TrieNode():

    def __init__(self, char: str = '') -> None:
        self.char = char
        self.children = []
        self.word_end = False

    def attach(self, node: 'TrieNode'):
        self.children.append(node)

    def get_child_character(self, char: str) -> Optional['TrieNode']:
        for child in self.children:
            if char == child.char:
                return child
        return None

    def print_children(self, s: str = '') -> None:
        s += self.char
        if self.word_end:
            print(s)
        for child in self.children:
            child.print_children(s)


class Trie():

    def __init__(self) -> None:
        self.root = TrieNode()

    def add_word(self, word: str, current_node: TrieNode) -> None:
        c = word[:1]
        if c == '':
            current_node.word_end = True
            return
        child_node = current_node.get_child_character(c)
        if child_node:
            self.add_word(word[1:], child_node)
        else:
            new_node = TrieNode(c)
            current_node.attach(new_node)
            self.add_word(word[1:], new_node)

    def print(self) -> None:
        self.root.print_children()

    def check_word(self, word: str, current_node: TrieNode) -> True:
        if word == '' and current_node.word_end:
            return True
        child_node = current_node.get_child_character(word[:1])
        if child_node:
            return self.check_word(word[1:], child_node)
        return False


def is_word(s: str) -> bool:
    """
    Check if provided string is a valid word.
    """
    return s in WORD_DICT


def find_all_words(grid: List[List[str]]) -> None:
    """
    Given the provided letter grid, print all words.
    """
    visited = [[False for x in grid] for y in grid[0]]
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            find_words(x, y, grid, visited, '')


def find_words(x: int,
               y: int,
               grid: List[List[str]],
               visited: List[List[bool]],
               s: str) -> None:
    """
    Recursive function; based on a position, check if current string is
    a word and iterate across neighbouring positions.
    """
    visited[x][y] = True
    s += grid[x][y]

    if is_word(s):
        print(s)

    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            if (i >= 0 and i < len(grid)) and (j >= 0 and j < len(grid[0])):
                if not visited[i][j]:
                    find_words(i, j, grid, visited, s)

    s = s[:-1]
    visited[x][y] = False


def find_all_words_trie(grid: List[List[str]]) -> None:
    """
    Find all words using a trie based method.
    """
    visited = [[False for x in grid] for y in grid[0]]
    trie = Trie()
    for word in WORD_DICT:
        trie.add_word(word, trie.root)

    for x in range(len(grid)):
        for y in range(len(grid[0])):
            child = trie.root.get_child_character(grid[x][y])
            if child:
                find_words_trie(x, y, child, grid, visited, '')


def find_words_trie(x: int,
                    y: int,
                    node: TrieNode,
                    grid: List[List[str]],
                    visited: List[List[bool]],
                    s: str) -> None:
    s += grid[x][y]
    visited[x][y] = True

    if is_word(s):
        print(s)

    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            if (i >= 0 and i < len(grid)) and (j >= 0 and j < len(grid[0])):
                child = node.get_child_character(grid[i][j])
                if not visited[i][j] and child:
                    find_words_trie(i, j, child, grid, visited, s)

    s = s[:-1]
    visited[x][y] = False


TEST_RUNS = 1000


def test_dfs() -> None:
    for i in range(TEST_RUNS):
        find_all_words(GRID)


def test_trie() -> None:
    for i in range(TEST_RUNS):
        find_all_words_trie(GRID)


def main():
    find_all_words(GRID)
    find_all_words_trie(GRID)
    cProfile.run('test_trie()', 'test_trie_output.txt')
    cProfile.run('test_dfs()', 'test_dfs_output.txt')


if __name__ == '__main__':
    main()
