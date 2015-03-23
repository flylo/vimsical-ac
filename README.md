# vimsical-ac
topic mining and word completion (maybe eventually suggestion) module

## current method idea
1. topic model on corpus
2. build autocorrect on top 75% of words in each topic in corpus
3. predict topic of last n sentences
4. use appropriate autocorrect function
5. compare accuracy with no topic
if there is no lift, then topics are likely a dead-end

old notes:
* system will be aware of high level topic of last n sentences
* topic will be taken into account when serving maximum likelihood word completion
  * online incrementing of sentence-level topic score for each word using word_topic_mappings mongo collection
  * sentences (or groups of sentences) will be evaluated as belonging to a topic and topic-based language models will exist in a DB to 
* system will be tested on holdout sample in corpus and tuned accordingly
* recomputing of model to be done on server side
* possible sources
  * http://blog.javascriptroom.com/2013/01/21/markov-chains/
    * http://stackoverflow.com/questions/14816100/convert-text-prediction-script-markov-chain-from-javascript-to-python
  * http://www.peterbouda.eu/pressagio-a-predictive-text-system-in-python.html
  * http://blog.qbox.io/multi-field-partial-word-autocomplete-in-elasticsearch-using-ngrams
  * http://pythonhosted.org/pyenchant/api/enchant.html
  * http://norvig.com/spell-correct.html
    * could compute probable n-grams within each topic to avoid having to process millions of word combination