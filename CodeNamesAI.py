from init import *

class CodeNameAI:
    def __init__(self, path, rules, weights=(8,1,2,5)):
        #Import model
        self.model_ini = KeyedVectors.load_word2vec_format(path, binary=True, unicode_errors="ignore")
        #Build dictionnary
        self.word2vec = {}
        for k,v in self.model_ini.key_to_index.items():
            split_k = k.split("_")
            if any(not c.isalnum() for c in split_k[0]):
                if not ("-" in split_k[0] or "'" in split_k[0]):
                    continue
            if v<10000 and len(split_k[-1])==1 and split_k[-1]!=['p','c','d'] and len(split_k[0]) > 1:
                self.word2vec[split_k[0]] = self.model_ini.get_vector(k)
        self.hints_to_remember = []
        self.rules = rules
        self.weights = weights

    def update_grid(self, grid, grid_labels):
        for i in range(len(grid)):
            w = grid[i]
            if w not in self.word2vec.keys() and w is not None:
                grid[i] = difflib.get_close_matches(w, self.word2vec.keys(), n=1, cutoff=0.5)[0]
                print("WARNING : Word not found in model: " + w + " replaced by " + grid[i])
                grid_labels[i//5][i%5].config(text=grid[i])

    def get_action(self, hint, grid):
        changed_words = {}
        for i in range(len(grid)):
            w = grid[i]
            if w not in self.word2vec.keys() and w is not None:
                grid[i] = difflib.get_close_matches(w, self.word2vec.keys(), n=1, cutoff=0.5)[0]
                print("WARNING : Word not found in model: " + w + " replaced by " + grid[i])
                changed_words[grid[i]] = w
        if hint not in self.word2vec.keys():
            n_hint = difflib.get_close_matches(hint, self.word2vec.keys(), n=1, cutoff=0.5)[0]
            print("WARNING : Hint not found in model: " + hint + " replaced by " + n_hint)
            hint = n_hint
        similarities = []
        for w in grid:
            if w is not None:
                similarities.append(self.cosine_similarity(self.word2vec[w], self.word2vec[hint]))
            else:
                similarities.append(-math.inf)
        similarities = np.array(similarities)
        answers = [(grid[ind],similarities[ind]) for ind in similarities.argsort()[-25:][::-1]]
        if answers[0][0] in changed_words.keys():
            return changed_words[answers[0][0]], answers
        return answers[0][0], answers

    def weight(self, length):
        if length == 1:
            return 1
        elif length == 2:
            return 1.1
        elif length == 3:
            return 0.75
        elif length == 4:
            return 0.5


    def get_hint_combination(self, grid, good_ind, neutrals_ind, negatives_ind, murderer_ind):
        scores = [(self.get_hint_lists(grid, subset, neutrals_ind, negatives_ind, murderer_ind)[0],
                   len(subset)) for subset in self.all_subsets(good_ind) if len(subset)<5]
        scores.sort(key=lambda x: x[0][0], reverse=True)
        return scores[0][0][1], scores[0][1]

    def get_hint_lists(self, grid, test, neutrals_ind, negatives_ind, murderer_ind):
        scores = self.most_similar([self.word2vec[grid[g]] for g in test],
                                [self.word2vec[grid[g]] for g in neutrals_ind],
                                [self.word2vec[grid[g]] for g in negatives_ind],
                                self.word2vec[grid[murderer_ind]])
        scores = [t for t in scores if self.rules(t[1])]
        return scores

    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (norm(a) * norm(b))

    def all_subsets(self, ss):
        return chain(*map(lambda x: combinations(ss, x), range(1, len(ss) + 1)))

    def most_similar(self, positives, neutrals, negatives, murderer):
        a, b, c, d = self.weights
        mean_vector = a*np.sum(positives,axis=0) - b*np.sum(neutrals, axis=0) - c*np.sum(negatives, axis=0) - d*murderer
        mean_vector /= a*len(positives) + b*len(neutrals) + c*len(negatives) - d*1
        scores = [(self.weight(len(positives))*self.cosine_similarity(self.word2vec[w], mean_vector),w) for w in self.word2vec]
        scores.sort(key=lambda x: x[0], reverse=True)
        return scores

    def most_similar_simple(self, w2v, positives, murderer):
        mean_vector = np.sum(positives,axis=0) - murderer
        mean_vector /= len(positives) - 1
        scores = [(self.cosine_similarity(self.word2vec[w], mean_vector),w) for w in w2v]
        scores.sort(key=lambda x: x[0], reverse=True)
        return scores