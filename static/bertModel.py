from transformers import BertTokenizer, BertForMaskedLM
import torch
import nltk
import logging
from itertools import chain
import math
import numpy as np
from nltk import word_tokenize
from typing import Tuple, List, Dict
from copy import deepcopy
import math
# from tqdm import tqdm


nltk.download('punkt')
# LOG = logging.getLogger('bert')
# LOG.addHandler(logging.NullHandler())


def convert_suggestions_to_list(suggestionString):
    suggestionList = suggestionString.replace("\'", '\"')
    suggestionList = suggestionList.split('\"')
    suggestionList = [suggestionList[a]
                      for a in range(1, len(suggestionList), 2)]
    return suggestionList


class PersianMaskedModel:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained(
            'Model/bert-base-parsbert-uncased')
        self.bertMaskedLM = BertForMaskedLM.from_pretrained(
            'Model/bert-base-parsbert-uncased', return_dict=True)

    def find_first_index_of_word(self, token_map: dict, word_index: int) -> int:
        return (
            len(
                list(
                    chain.from_iterable(
                        [
                            vals for key, vals in token_map.items() if key < word_index
                        ]
                    )
                )
            )
            + 1
        )

    def get_masked_sentence_score(self, indexed_tokens: list) -> torch.tensor:
        torch.set_grad_enabled(False)
        self.bertMaskedLM.eval()

        softmax = torch.nn.Softmax(dim=1)
        with torch.no_grad():
            tokens_tensor = torch.tensor([indexed_tokens])
            segments_tensors = torch.tensor(
                [torch.zeros(len(indexed_tokens), dtype=int).tolist()]
            )
            outputs = self.bertMaskedLM(
                tokens_tensor, token_type_ids=segments_tensors)
            predictions = softmax(outputs[0].squeeze(0))

        return predictions

    def tokenize_sentence(self, token_map: dict) -> list:
        start_token_id = self.tokenizer.encode(
            "[CLS]", add_special_tokens=False)
        end_token_id = self.tokenizer.encode("[SEP]", add_special_tokens=False)
        the_tokens = list(chain.from_iterable(token_map.values()))

        return list(start_token_id) + the_tokens + list(end_token_id)

    def get_word_prediction_score(
        self,
        tokens_to_predict,
        predictions,
        starting_position,
    ) -> Tuple[Tuple[str, float], ...]:

        if len(tokens_to_predict) == 1:
            return tuple([predictions[starting_position][tokens_to_predict].item()])

        return tuple(
            [
                (
                    self.tokenizer.convert_ids_to_tokens(tmp),
                    predictions[starting_position][tmp].item(),  # type: ignore
                )
                for idx, tmp in enumerate(tokens_to_predict)
            ]
        )  # type: ignore

    def get_words_in_sentence_probability(
        self,
        sentence: str,
        words: list,
        word_index: int,
    ) -> Tuple[Tuple[str, float], ...]:

        whole_tokens = word_tokenize(sentence)

        bert_token_map = {
            idx: self.tokenizer.encode(whole_token, add_special_tokens=False)
            for idx, whole_token in enumerate(whole_tokens)
        }  # type: Dict[int,List[int]]

        mask_token_id = self.tokenizer.encode(
            "[MASK]", add_special_tokens=False)

        words_tokens_to_predict = {}
        for word in words:
            words_tokens_to_predict[word] = self.tokenizer.encode(
                word, add_special_tokens=False)

        bert_token_map[word_index] = mask_token_id * 1

        indexed_tokens = self.tokenize_sentence(bert_token_map)

        predictions = self.get_masked_sentence_score(indexed_tokens)

        # to find the true index of the desired word; count all of the tokens and subtokens before
        starting_position = self.find_first_index_of_word(
            bert_token_map, word_index)
        word_probs = []
        for word, tokens_to_predict in words_tokens_to_predict.items():
            word_probs.append((word, self.get_word_prediction_score(
                tokens_to_predict, predictions, starting_position)))

        return word_probs

    def sum_log_probabilities_word(self, results: Tuple, boost_factor: int = 1) -> float:
        if(len(results) > 1):
            return sum([math.log(tmp[1] * boost_factor) for tmp in results])

        else:
            return math.log(results[0]*boost_factor)

    def calculate_probability(self, sentenceMask: str, targets: list):
        # TODO: it can't find mask if it gets appended to other symbols such as dot --> fix this
        mask_index = sentenceMask.split().index(self.tokenizer.mask_token)
        # suggestion_words = convert_suggestions_to_list(targets)
        # print(suggestion_words)

        sentence = sentenceMask.replace(self.tokenizer.mask_token, 'یکانان')
        words_probabilities = self.get_words_in_sentence_probability(
            sentence, targets,  word_index=mask_index)
        results_log = []
        # print('-------------------------------start---------------------------------------')
        # print(f'{sentenceMask} \n{targets}')
        for target_word in words_probabilities:
            results_log.append(
                (target_word[0], self.sum_log_probabilities_word(target_word[1])))
        # print('-------------------------------end-----------------------------------------')

        return sorted(results_log, key=lambda x: x[1])
