from core.types import ElasticsearchAnswer


class Utils():
    
    def merge_two_ElasticsearchAnswer_lists(
        self, 
        answer1: ElasticsearchAnswer, 
        answer2: ElasticsearchAnswer
    ) -> ElasticsearchAnswer:

        items_dict = {}
        for item in answer1.hits :
            key = item.id
            items_dict[key] = item
        for item in answer2.hits :
            key = item.id
            if key not in items_dict:
                items_dict[key] = item
        
        merged_answer = ElasticsearchAnswer(hits=list(items_dict.values()))
        return merged_answer