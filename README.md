# vimsical-ac
topic mining and word completion (maybe eventually suggestion) module

* system will be aware of high level topic of last n sentences
* topic will be taken into account when serving maximum likelihood word completion
  * online incrementing of sentence-level topic score for each word using word_topic_mappings mongo collection
* system will be tested on holdout sample in corpus and tuned accordingly
* recomputing of model to be done on server side