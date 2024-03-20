try:
    import os
    import re
    import sys
    import requests
    import argparse as ap
    import threading as th
    import collections as col
    import matplotlib.pyplot as plt
except ModuleNotFoundError as e:
    print(f"Error: {e}")
    exit(1)


def get_url(url):
    return requests.get(url).text


def map_function(text, result_list):
    words = re.findall(r'\w+', text.lower())
    result_list.append(col.Counter(words))


def reduce_function(mapping_list):
    return sum(mapping_list, col.Counter())


def chunkify(text, num_chunks):
    chunk_size = len(text) // num_chunks
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def map_reduce(text, num_threads=4):
    chunks = chunkify(text, num_threads)
    result_list = []

    threads = []
    for chunk in chunks:
        t = th.Thread(target=map_function, args=(chunk, result_list))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()

    reduced = reduce_function(result_list)
    return reduced


def visualize_top_words(word_counts, top=10):
    top_words = word_counts.most_common(top)
    top_words.sort(key=lambda x: x[1])
    words, counts = zip(*top_words)
    plt.barh(words, counts)
    plt.xlabel('Frequency')
    plt.ylabel('Words')
    plt.title(f'Top {top} Most Frequent Words in Text')
    plt.xticks(rotation=45)
    plt.show()


def cli():
    parser = ap.ArgumentParser(
        description='Analysing a web page using the MapReduce model')
    parser.add_argument('--url', '-u', required=True, type=str,
                        help='Address of the http web page for analysis')
    parser.add_argument('--words', '-w', required=False, type=int, default=10,
                        help='Number of top words to analyse (default: %(default)s)')
    parser.add_argument('--threads', '-t', required=False, type=int,
                        default=5, help='Number of threads to use (default: %(default)s)')

    return parser.parse_args()


def main():
    args = cli()
    text = get_url(args.url)
    word_counts = map_reduce(text, args.threads)
    visualize_top_words(word_counts, args.words)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\nGood bye!")
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
