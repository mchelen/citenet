from backend.api import search


class Crawler(object):

    def __init__(self):
        self.unwalked = []
        self.all = {}
        self.iteration_counter = 0

    def crawl(self, initial_id, max_iters):
        '''Start crawling.
               initial_id: pubmed id of the paper where the crawling
                           starts.
                max_iters: maximum number of iteration, these bascically
                           correspond to the number of API calls. not
                           to be confused with 'generations'.

        '''

        self.all[initial_id] = (search(initial_id))[0]
        self.crawl_rec(initial_id, max_iters)
        return self.all

    def crawl_rec(self, initial_id, max_iters):
        '''Recrive crawling.
               initial_id: pubmed id of the paper where the crawling
                           starts.
                max_iters: maximum number of iteration, these bascically
                           correspond to the number of API calls. not
                           to be confused with 'generations'.

        '''

        for reference in self.get_references(initial_id):
            self.append_child(reference)
            self.all[initial_id].references.append(reference.api_id)

        for target in self.pick_next_targets():
            if self.iteration_counter < max_iters:
                self.iteration_counter += 1
                self.crawl_rec(target.api_id, max_iters)

    def get_references(self, api_id):
        '''Get all references for an id, for now the pubmed id.
        '''

        return search(api_id, True)

    def append_child(self, child):
        '''Updates the papers in the unwalked list and all dict. Also
           updates the local_citation_count.
               child: new paper object.

        '''

        if not child.api_id in self.all:
            self.unwalked.append(child)
            self.all[child.api_id] = child
        else:
            self.all[child.api_id].local_citation_count += 1

    def pick_next_targets(self):
        '''Defines how the papers to be crawled next are selected from
           the uncrawled paper list. All papers that have the highest
           citation count in the local network are returned. There can
           be can be several papers have the same citation count.

        '''

        targets = []

        if self.unwalked:
            self.unwalked.sort(key=lambda paper: paper.local_citation_count,
                               reverse=True)

            highest_citation_count = self.unwalked[0].local_citation_count

            for paper in self.unwalked:

                if paper.local_citation_count == highest_citation_count:
                    targets.append(paper)
                else:
                    break

        for target in targets:
            self.unwalked.remove(target)

        return targets

