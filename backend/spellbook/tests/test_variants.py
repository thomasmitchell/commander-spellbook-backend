from django.test import TestCase
from spellbook.variants.variant_trie import VariantTrie
from spellbook.variants.list_utils import rotate, all_rotations, merge_sort_unique, merge_identities, includes_any


def list_of_tuples_of_lists_to_set(list_of_tuples_of_lists: list[tuple[list]]) -> set[tuple[tuple]]:
    return set([tuple([tuple(x) for x in y]) for y in list_of_tuples_of_lists])


class ListUtilsTests(TestCase):

    def test_rotate(self):
        self.assertEqual(rotate([1, 2, 3], 0), [1, 2, 3])
        self.assertEqual(rotate([1, 2, 3], 1), [3, 1, 2])
        self.assertEqual(rotate([1, 2, 3], 5), [2, 3, 1])
        self.assertEqual(rotate([1, 2, 3], 6), [1, 2, 3])
        self.assertEqual(rotate([1, 2, 3, 4, 5], -1), [2, 3, 4, 5, 1])
        self.assertEqual(rotate([1, 2, 3, 4, 5], -2), [3, 4, 5, 1, 2])
        self.assertEqual(rotate([1, 2, 3, 4, 5], -9), [5, 1, 2, 3, 4])
        self.assertEqual(rotate(['a', ['x'], {'a'}], 5), [['x'], {'a'}, 'a'])
        self.assertEqual(rotate(['a', ['x'], {'a'}], 6), ['a', ['x'], {'a'}])
        self.assertEqual(rotate(['a', ['x'], {'a'}, 4, 5], -1), [['x'], {'a'}, 4, 5, 'a'])
        self.assertEqual(rotate(['a', ['x'], {'a'}, 4, 5], -2), [{'a'}, 4, 5, 'a', ['x']])
        self.assertEqual(rotate(['a', ['x'], {'a'}, 4, 5], -3), [4, 5, 'a', ['x'], {'a'}])
        self.assertEqual(rotate((1, 2, 3), 0), (1, 2, 3))
        self.assertEqual(rotate((1, 2, 3), 1), (3, 1, 2))
        self.assertEqual(rotate((1, 2, 3), 5), (2, 3, 1))
        self.assertEqual(rotate((1, 2, 3), 6), (1, 2, 3))
        self.assertEqual(rotate((1, 2, 3, 4, 5), -1), (2, 3, 4, 5, 1))
        self.assertEqual(rotate((1, 2, 3, 4, 5), -2), (3, 4, 5, 1, 2))
        self.assertEqual(rotate((1, 2, 3, 4, 5), -8), (4, 5, 1, 2, 3))
        self.assertEqual(rotate((1, 2, 3, 4, 5), -9), (5, 1, 2, 3, 4))
        self.assertEqual(rotate(('a', ['x'], {'a'}), 5), (['x'], {'a'}, 'a'))
        self.assertEqual(rotate(('a', ['x'], {'a'}), 6), ('a', ['x'], {'a'}))
        self.assertEqual(rotate(('a', ['x'], {'a'}, 4, 5), -1), (['x'], {'a'}, 4, 5, 'a'))

    def test_all_rotations(self):
        self.assertEqual(all_rotations([1, 2, 3]), [[1, 2, 3], [3, 1, 2], [2, 3, 1]])
        self.assertEqual(all_rotations([1, 2, 3, 4, 5]), [[1, 2, 3, 4, 5], [5, 1, 2, 3, 4], [4, 5, 1, 2, 3], [3, 4, 5, 1, 2], [2, 3, 4, 5, 1]])
        self.assertEqual(all_rotations(['a', ['x'], {'a'}]), [['a', ['x'], {'a'}], [{'a'}, 'a', ['x']], [['x'], {'a'}, 'a']])
        self.assertEqual(all_rotations((1, 2, 3)), [(1, 2, 3), (3, 1, 2), (2, 3, 1)])

    def test_merge_sort_unique(self):
        self.assertEqual(merge_sort_unique([1, 2, 3], [4, 5, 6]), [1, 2, 3, 4, 5, 6])
        self.assertEqual(merge_sort_unique([1, 2, 3], [3, 4, 5]), [1, 2, 3, 4, 5])
        self.assertEqual(merge_sort_unique([1, 2, 3], [1, 2, 3]), [1, 2, 3])
        self.assertEqual(merge_sort_unique([1, 2, 3], [1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])
        self.assertEqual(merge_sort_unique([1, 2, 3, 4, 5], [1, 2, 3]), [1, 2, 3, 4, 5])
        self.assertEqual(merge_sort_unique([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])
        self.assertEqual(merge_sort_unique(['a', 'c', 'z'], ['b', 'd', 'y']), ['a', 'b', 'c', 'd', 'y', 'z'])
        self.assertEqual(merge_sort_unique((1, 2, 3), (4, 5, 6)), [1, 2, 3, 4, 5, 6])

    def test_merge_identities(self):
        self.assertEqual(merge_identities(['', '']), 'C')
        for c in 'CWUBRG':
            self.assertEqual(merge_identities([c, '']), c)
            self.assertEqual(merge_identities(['', c]), c)
            self.assertEqual(merge_identities([c, c]), c)
        self.assertEqual(merge_identities(['W', 'U']), 'WU')
        self.assertEqual(merge_identities(['W', 'U', 'B']), 'WUB')
        self.assertEqual(merge_identities(['W', 'U', 'B', 'R']), 'WUBR')
        self.assertEqual(merge_identities(['W', 'U', 'B', 'R', 'G']), 'WUBRG')
        self.assertEqual(merge_identities(sorted(['W', 'U', 'B', 'R', 'G'])), 'WUBRG')
        self.assertEqual(merge_identities(['W', 'U', 'B', 'R', 'G', 'W']), 'WUBRG')
        self.assertEqual(merge_identities(['WU', 'BR', 'G', 'WG']), 'WUBRG')
        self.assertEqual(merge_identities(['S']), 'C')
        self.assertEqual(merge_identities(['S', 'R']), 'R')
        self.assertEqual(merge_identities(['r', 'g']), 'RG')
        self.assertEqual(merge_identities(['g', 'r']), 'RG')

    def test_includes_any(self):
        self.assertTrue(includes_any({1, 2, 3}, [{1, 2, 3}]))
        self.assertTrue(includes_any({1, 2, 3}, [{1, 2, 3}, {1, 2, 3, 4}]))
        self.assertTrue(includes_any({1, 2, 3}, [{1, 2, 3, 4}, {2}]))
        self.assertTrue(includes_any(set(), [set()]))
        self.assertTrue(includes_any({1}, [{2}, {1}]))


class VariantTrieTests(TestCase):

    def test_ingredients_to_key(self):
        trie = VariantTrie()
        self.assertEqual(trie.key_to_ingredients(trie.ingredients_to_key([1, 2, 3, 4], [])), ([1, 2, 3, 4], []))
        self.assertEqual(trie.key_to_ingredients(trie.ingredients_to_key([1, 2, 3, 4], [1, 2, 3])), ([1, 2, 3, 4], [1, 2, 3]))
        self.assertEqual(trie.key_to_ingredients(trie.ingredients_to_key([], [1, 2, 3])), ([], [1, 2, 3]))
        self.assertEqual(trie.key_to_ingredients(trie.ingredients_to_key([], [])), ([], []))
        self.assertEqual(trie.key_to_ingredients(trie.ingredients_to_key([1], [1])), ([1], [1]))

    def test_variant_trie_add(self):
        trie = VariantTrie()
        trie.add([1, 2, 3, 4], [1, 2, 3])
        self.assertEqual(trie.variants(), [([1, 2, 3, 4], [1, 2, 3])])
        trie.add([1, 2, 3, 4], [1, 2, 3])
        self.assertEqual(trie.variants(), [([1, 2, 3, 4], [1, 2, 3])])
        trie.add([1, 2, 3, 4], [1, 2, 3, 4])
        self.assertEqual(trie.variants(), [([1, 2, 3, 4], [1, 2, 3])])
        trie.add([1, 2, 3, 4, 5], [1, 2, 3])
        self.assertEqual(trie.variants(), [([1, 2, 3, 4], [1, 2, 3])])
        trie.add([1, 2, 3, 4, 5, 6], [1, 2])
        self.assertEqual(trie.variants(), [([1, 2, 3, 4], [1, 2, 3]), ([1, 2, 3, 4, 5, 6], [1, 2])])
        trie.add([1, 2, 3, 4, 5], [1, 2])
        self.assertEqual(trie.variants(), [([1, 2, 3, 4], [1, 2, 3]), ([1, 2, 3, 4, 5], [1, 2])])

    def test_variant_trie_or(self):
        trie = VariantTrie()
        trie.add([1, 2, 3, 4], [1, 2, 3])
        trie.add([1, 2, 3, 4, 5], [1, 2])
        trie2 = VariantTrie()
        trie2.add([1, 2, 3], [1, 2, 3, 4])
        trie2.add([1, 2, 3, 4, 5], [1])

        trie3 = trie | trie2
        self.assertEqual(trie3.variants(), [([1, 2, 3, 4], [1, 2, 3]), ([1, 2, 3, 4, 5], [1]), ([1, 2, 3], [1, 2, 3, 4])])
        trie4 = trie2 | trie
        self.assertSetEqual(list_of_tuples_of_lists_to_set(trie3.variants()), list_of_tuples_of_lists_to_set(trie4.variants()))

    def test_variant_trie_and(self):
        trie = VariantTrie()
        trie.add([1, 2, 3, 4], [1, 2, 3])
        trie.add([1, 2, 3, 4, 5], [1, 2])
        trie2 = VariantTrie()
        trie2.add([1, 2, 3], [1, 2, 3, 4])
        trie2.add([1, 2, 3, 4, 5], [1])

        trie3 = trie & trie2
        self.assertEqual(trie3.variants(), [([1, 2, 3, 4], [1, 2, 3, 4]), ([1, 2, 3, 4, 5], [1, 2])])
        trie4 = trie2 & trie
        self.assertSetEqual(list_of_tuples_of_lists_to_set(trie3.variants()), list_of_tuples_of_lists_to_set(trie4.variants()))