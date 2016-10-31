from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import Counter

# Define constants associated with the usual special-case tokens.
PAD_ID = 0
GO_ID = 1
EOS_ID = 2

PAD_TOKEN = "PAD"
EOS_TOKEN = "EOS"
GO_TOKEN = "GO"


class DataReader(object):

    def __init__(self, train_path, config, special_tokens=(), dataset_copies=1):
        self.config = config
        self.dataset_copies = dataset_copies

        # Construct vocabulary.
        max_vocabulary_size = self.config.max_vocabulary_size
        token_counts = Counter()

        for tokens in self.read_tokens(train_path):
            token_counts.update(tokens)

        self.token_counts = token_counts

        # Get to max_vocab_size words
        count_pairs = sorted(token_counts.items(), key=lambda x: (-x[1], x[0]))
        vocabulary, _ = list(zip(*count_pairs))
        vocabulary = list(vocabulary)
        # Insert the special tokens at the beginning.
        vocabulary[0:0] = special_tokens
        self.token_to_id = dict(
            zip(vocabulary[:max_vocabulary_size], range(max_vocabulary_size)))
        self.id_to_token = {v: k for v, k in self.token_to_id.items()}

    def read_tokens(self, path):
        """
        Reads the given file line by line and yields the list of tokens present
        in each line.

        :param path:
        :return:
        """
        raise NotImplementedError("Must implement read_tokens")

    def read_token_samples(self, path):
        """
        Reads the given file line by line and yields the word-form of each
        derived sample.

        :param path:
        :return:
        """
        raise NotImplementedError("Must implement read_word_samples")

    def convert_token_to_id(self, word):
        """

        :param word:
        :return:
        """
        raise NotImplementedError("Must implement convert_word_to_id")

    def convert_id_to_token(self, word_id):
        """

        :param i
        :return:
        """
        raise NotImplementedError("Must implement convert_word_to_id")

    def sentence_to_token_ids(self, sentence):
        """
        Converts a whitespace-delimited sentence into a list of word ids.
        """
        return [self.convert_token_to_id(word) for word in sentence.split()]

    def token_ids_to_sentence(self, word_ids):
        """
        Converts a list of word ids to a space-delimited string.
        """
        return " ".join([self.convert_id_to_token(word) for word in word_ids])

    def read_samples(self, path):
        """

        :param path:
        :return:
        """
        for source_words, target_words in self.read_token_samples(path):
            source = [self.convert_token_to_id(word) for word in source_words]
            target = [self.convert_token_to_id(word) for word in target_words]
            target.append(EOS_ID)

            yield source, target

    def build_dataset(self, path):
        dataset = [[] for _ in self.config.buckets]

        # Make multiple copies of the dataset so that we synthesize different
        # dropouts.
        for _ in range(self.dataset_copies):
            for source, target in self.read_samples(path):
                for bucket_id, (source_size, target_size) in enumerate(
                        self.config.buckets):
                    if len(source) < source_size and len(
                            target) < target_size:
                        dataset[bucket_id].append([source, target])
                        break

        return dataset

