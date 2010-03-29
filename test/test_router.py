import unittest
import bottle
import itertools

class TestParser(unittest.TestCase):
    def testTokenier(self):
        ''' This tests the complete specrum of possible wildcard syntax
            variations '''
        head = ('head','') # head | no head
        delim = ('', ':','::',':::') # no | real | escaped | escaped+real
        name = ('name','') # named | anonymous
        regexp = ('','#reg#','##') # default | specified | empty
        tail = ('tail', ';tail', '') # tail | non-alnum tail | no tail
        combinations = itertools.product(head, delim, name, regexp, tail)

        for head, delim, name, regexp, tail in combinations:
            route = ''.join((head, delim, name, regexp, tail))
            result = list(bottle.Route(route, 'target').tokens)
            if len(delim) % 2: # This produces a wildcard token
                # Alpha-numeric tails merge with the name
                # if they are not separated by a regexp
                if tail.isalnum() and not regexp:
                    name, tail = name + tail, ''
                # The '#' chars are not part of the regexp
                # and empty or missing regexps default to `None`
                regexp = regexp[1:-1] if len(regexp) > 2 else None
                # Anonymous routes have `None` as a name
                name = name or None
                # Escaped delimiters are part of the head
                head += ':' * (len(delim) // 2)
                reference = [head, (name, regexp), tail]
            else: # Escaped wildcard
                reference = [route.replace('::',':')]
            self.assertEqual(reference, result)


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.r = r = bottle.Router()

    def testBasic(self):
        add = self.r.add
        match = self.r.match
        add('/static', 'static')
        self.assertEqual(('static', {}), match('/static'))
        add('/::its/:#.+#/:test/:name#[a-z]+#/', 'handler')
        self.assertEqual(('handler', {'test': 'cruel', 'name': 'world'}),
                         match('/:its/a/cruel/world/'))
        add('/:test', 'notail')
        self.assertEqual(('notail', {'test': 'test'}), match('/test'))
        add(':test/', 'nohead')
        self.assertEqual(('nohead', {'test': 'test'}), match('test/'))
        add(':test', 'fullmatch')
        self.assertEqual(('fullmatch', {'test': 'test'}), match('test'))
        add('/:#anon#/match', 'anon')
        self.assertEqual(('anon', {}), match('/anon/match'))
        self.assertEqual((None, {}), match('//no/m/at/ch/'))

    def testErrorInPattern(self):
        self.assertRaises(bottle.RouteSyntaxError, self.r.add, '/:bug#(#/', 'buggy')

    def testBuild(self):
        add = self.r.add
        build = self.r.build
        add('/:test/:name#[a-z]+#/', 'handler', name='testroute')
        add('/anon/:#.#', 'handler', name='anonroute')
        url = build('testroute', test='hello', name='world')
        self.assertEqual('/hello/world/', url)
        self.assertRaises(bottle.RouteBuildError, build, 'test')
        # RouteBuildError: No route found with name 'test'.
        self.assertRaises(bottle.RouteBuildError, build, 'testroute')
        # RouteBuildError: Missing parameter 'test' in route 'testroute'
        #self.assertRaises(bottle.RouteBuildError, build, 'testroute', test='hello', name='1234')
        # RouteBuildError: Parameter 'name' does not match pattern for route 'testroute': '[a-z]+'
        #self.assertRaises(bottle.RouteBuildError, build, 'anonroute')
        # RouteBuildError: Anonymous pattern found. Can't generate the route 'anonroute'.

if __name__ == '__main__':
    unittest.main()
