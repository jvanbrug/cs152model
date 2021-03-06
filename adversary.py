from database import Network
from math import exp


class Adversary:
    """Adversarial analyst that reconstructs the database from repeated queries

    :param curator: curator of the target network
    :param float eta: multiplicative weights update power (w <-- w * e^eta)
    :ivar curator: curator of the target network
    :ivar float eta: multiplicative weights update power (w <-- w * e^eta)
    :ivar network: the approximation network
    :ivar tuple preference_combinations: all possible preference tuples
    :ivar int preference_index: index of next preference tuple to pirate
    """

    def __init__(self, curator, eta=1e-4):
        self.curator = curator
        self.eta = eta
        self.network = Network(size=self.curator.network.size,
                               interactivity=self.curator.network.interactivity)
        self.network.make_all_links()
        self.preference_combinations = self.network.get_all_preferences()
        self.preference_index = 0

    @staticmethod
    def normalize(utilities):
        utility_sum = sum(utilities)
        return [1.0 * utility / utility_sum for utility in utilities]

    def pirate(self, sequence_length, number_of_queries=1):
        """Return a network that approximates curator's network probabilities

        This network's link utilities are normalized to probabilities, rather
        than fed through the exponential mechanism to obtain probabilities.

        :param int sequence_length: length of sequences to pirate
        :param int number_of_queries: number of times to query the curator
        """
        progress_bar_size = 50
        progress_bar_step = 2
        print 'Pirating %d' % number_of_queries, '|' + ' ' * progress_bar_size + '|',
        for query_number in range(number_of_queries):
            if not query_number % (number_of_queries * progress_bar_step / 100.0) and query_number:
                progress_percent = int(100 * query_number / number_of_queries)
                print('\rPirating %d\t|' % number_of_queries +
                      '-' * (progress_percent * progress_bar_size / 100) +
                      ' ' * ((100 - progress_percent) * progress_bar_size / 100) + '|'),
            preferences = self.preference_combinations[self.preference_index]
            query_response = self.curator.query(sequence_length, preferences)
            sequence = [node for node in self.network.nodes for name in query_response
                        if node.name == name]
            # Update all seen links by multiplicative weights
            for i in range(len(sequence) - 1):
                node1, node2 = sequence[i], sequence[i + 1]
                preference = preferences[self.network.nodes.index(node1)]
                link = node1.links[node2][preference]
                link.utility *= exp(self.eta)
            self.preference_index += 1
            self.preference_index %= len(self.preference_combinations)
        print '\rPirating %d\t|' % number_of_queries + '-' * progress_bar_size + '|'
