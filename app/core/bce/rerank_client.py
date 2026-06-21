from BCEmbedding import RerankerModel


class RerankClient:
    def __init__(self,rerank_model) -> None:
        self.model = RerankerModel(rerank_model,
                                   trust_remote_code=True,)
    def rerank(self,query,massages):
        sentence_pairs = [[query, massage] for massage in massages]
        #scores = self.model.compute_score(sentence_pairs)
        rerank_results = self.model.rerank(query, massages)
        return rerank_results
    