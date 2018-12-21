import pickle
from model.utils import get_dfa
from pathlib import Path
# import pdb

def get_graph(args, method='reduced'):
    """
    method: string, can be either 'reduced' or 'vanilla'
    """
    assert method in ['reduced', 'vanilla']

    cache_dir = Path(args.cache)
    cache_dir.mkdir(parents=True, exist_ok=True)

    if args.new or not (cache_dir/args.dfa).exists():
        n, edges, start, accepts, state2idx = get_dfa()
        pickle.dump((n, edges, start, accepts, state2idx), open(str(cache_dir/args.dfa), 'wb'))
    else:
        n, edges, start, accepts, state2idx = pickle.load(open(str(cache_dir/args.dfa), 'rb'))     

    if method == 'reduced':
        from model.renode import ReNode, ReLeaf
        graph = {}
        for i in range(n):
            graph[i] = {}
            for j in range(n):
                if i==j:
                    graph[i][j] = ReLeaf('ε')
                else:
                    graph[i][j] = ReLeaf(None)
        for edge in edges:
            i = state2idx[edge[0]]
            j = state2idx[edge[1]]
            graph[i][j] = graph[i][j].Or(ReLeaf(edge[2]))

        return graph, start, accepts, state2idx

    if method == 'vanilla':
        from model.renodeVanilla import ReNodeVanilla as ReNode
        graph = {}
        for i in range(n):
            graph[i] = {}
            for j in range(n):
                if i==j:
                    graph[i][j] = ReNode('ε')
                else:
                    graph[i][j] = ReNode(None)

        for edge in edges:
            i = state2idx[edge[0]]
            j = state2idx[edge[1]]
            graph[i][j] = graph[i][j].Or(ReNode(edge[2]))

        return graph, start, accepts, state2idx

def run(graph, verbose, display=True):
    for k in range(len(graph)):
        for i in range(len(graph)):
            for j in range(len(graph)):
                if verbose>=1:
                    print("k={}, i={}, j={}".format(k,i,j))
                a = graph[i][k].Concat(graph[k][k].Star())
                if verbose>=2:
                    print("graph[{}][{}] + graph[{}][{}]* = {} + {} = {}".format(i,k,k,k,graph[i][k],graph[k][k].Star(),a))
                b = a.Concat(graph[k][j])
                if verbose>=2:
                    print("a + graph[{}][{}] = {} + {} = {}".format(k,j,a,graph[k][j],b))
                c = graph[i][j].Or(b)
                if verbose>=2:
                    print("graph[{}][{}] | b = {} | {} = {}".format(i,j,graph[i][j],b,c))
                    print('-'*10)
                graph[i][j] = c
        if verbose>=2:
            print('='*20)

    if display:
        for i in range(len(graph)):
            for j in range(len(graph)):
                print(graph[i][j], end=' ')
            print('')

        

if __name__ == '__main__':
    import argparse
    # from IPython import embed

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', type=int, default=0, help='show extra information')
    parser.add_argument('--method', type=str, default='reduced', choices=['reduced', 'vanilla'], help='choose a method to convert dfa to regex')
    parser.add_argument('--dfa', type=str, default='cache.pkl', help="name of the dfa cache file")
    parser.add_argument('--new', action='store_true', help='whether to input a new dfa')
    parser.add_argument('--cache', type=str, default='./sampleDFA', help='directory to store dfa')
    args = parser.parse_args()

    graph, start, accepts, state2idx = get_graph(args, args.method)

    print('+'*20)

    run(graph, verbose=args.verbose, display=True)

    print('+'*20)

    node = graph[state2idx[start]][state2idx[accepts[0]]]
    for acc in accepts[1:]:
        node = node.Or(graph[state2idx[start]][state2idx[acc]])
    print(node)

    # embed()
