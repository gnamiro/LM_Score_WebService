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
from tqdm import tqdm


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

    def get_word_in_sentence_probability(
        self,
        sentence: str,
        word: str,
        bert_model: BertForMaskedLM,
        bert_tokenizer: BertTokenizer,
        word_index: int = -1,
    ) -> Tuple[Tuple[str, float], ...]:
        whole_tokens = word_tokenize(sentence)
        # whole_tokens = tokenizer.tokenize(sentence)
        print(whole_tokens)
        if word_index == -1:
            word_index = whole_tokens.index(word)
        bert_token_map = {
            idx: bert_tokenizer.encode(whole_token, add_special_tokens=False)
            for idx, whole_token in enumerate(whole_tokens)
        }  # type: Dict[int,List[int]]
        print(bert_token_map)
        mask_token_id = bert_tokenizer.encode(
            "[MASK]", add_special_tokens=False)
        tokens_to_predict = bert_tokenizer.encode(
            word, add_special_tokens=False)
        bert_token_map[word_index] = mask_token_id * \
            len(tokens_to_predict)  # type: ignore
        print(bert_token_map)
        # LOG.debug(
        #     "total bert tokens: %s whole tokens: %s",
        #     len(list(chain.from_iterable(bert_token_map.values()))),
        #     len(whole_tokens),
        # )
        torch.set_grad_enabled(False)
        bert_model.eval()
        # to find the true index of the desired word; count all of the tokens and subtokens before
        starting_position = (
            len(
                list(
                    chain.from_iterable(
                        [
                            vals for key, vals in bert_token_map.items() if key < word_index
                        ]  # type : ignore
                    )
                )
            )
            + 1
        )
        start_token_id = bert_tokenizer.encode(
            "[CLS]", add_special_tokens=False)
        end_token_id = bert_tokenizer.encode("[SEP]", add_special_tokens=False)
        the_tokens = list(chain.from_iterable(bert_token_map.values()))
        # LOG.debug(bert_tokenizer.convert_ids_to_tokens(the_tokens))
        indexed_tokens = list(start_token_id) + the_tokens + list(end_token_id)
        softmax = torch.nn.Softmax(dim=1)
        with torch.no_grad():
            # pylint: disable=not-callable,no-member
            tokens_tensor = torch.tensor([indexed_tokens])
            segments_tensors = torch.tensor(
                # type: ignore
                [torch.zeros(len(indexed_tokens), dtype=int).tolist()]
            )
            outputs = bert_model(
                tokens_tensor, token_type_ids=segments_tensors)
            predictions = softmax(outputs[0].squeeze(0))
        if len(tokens_to_predict) == 1:
            # type: ignore
            return tuple([predictions[starting_position][tokens_to_predict].item()])
        return tuple(
            [
                (
                    bert_tokenizer.convert_ids_to_tokens(tmp),
                    predictions[starting_position +
                                idx][tmp].item(),  # type: ignore
                )
                for idx, tmp in enumerate(tokens_to_predict)
            ]
        )  # type: ignore

    def sum_log_probabilities_word(self, results: Tuple, boost_factor: int = 100) -> float:
        if(len(results) > 1):
            return sum([math.log(tmp[1] * boost_factor) for tmp in results])

        else:
            return math.log(results[0]*boost_factor)

    def calculate_probability(self, sentenceMask: str, targets: list):
        mask_index = sentenceMask.split().index(self.tokenizer.mask_token)
        suggestion_words = convert_suggestions_to_list(targets)
        # print(suggestion_words)

        results_log = []

        for target_word in tqdm(suggestion_words, desc=f"bert_unmasker Processing [{sentenceMask}]:"):
            sentence = sentenceMask.replace(
                self.tokenizer.mask_token, 'یکانان')
            tmp = sentence.split()
            res = self.get_word_in_sentence_probability(
                sentence, target_word, bert_tokenizer=self.tokenizer, bert_model=self.bertMaskedLM, word_index=mask_index)
            results_log.append(
                (target_word, self.sum_log_probabilities_word(res)))

        return sorted(results_log, key=lambda x: x[1])
